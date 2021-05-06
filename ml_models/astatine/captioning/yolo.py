"""Image captioning module with YOLO"""

import logging
import math
import random

import torch
import cv2

import numpy as np

# Internal partial import
from .model import CaptionModule

logger = logging.getLogger("astatine.caps.yolo")

module = "SimpleYOLOModule"

def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clamp_(0, img_shape[1])  # x1
    boxes[:, 1].clamp_(0, img_shape[0])  # y1
    boxes[:, 2].clamp_(0, img_shape[1])  # x2
    boxes[:, 3].clamp_(0, img_shape[0])  # y2

def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords

def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    # Largely inspired by yolo's although we use lists and they
    # used tensors so we had to change the array indices
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[0] = x[0] - x[2] / 2  # top left x
    y[1] = x[1] - x[3] / 2  # top left y
    y[2] = x[0] + x[2] / 2  # bottom right x
    y[3] = x[1] + x[3] / 2  # bottom right y
    return y

class SimpleYOLOModule(CaptionModule):
    def __init__(self):
        logger.debug("Initializing")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, force_reload=False).autoshape()

    def process(self, img):
        detections = self.model([str(img)])
        names = detections.names
        pred = detections.xywhn[0]
        description = ""
        if len(pred) == 0:
            return description

        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

        #p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)
        #p = Path(p)  # to Path
        #save_path = str(save_dir / p.name)  # img.jpg
        #txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
        #s += '%gx%g ' % img.shape[2:]  # print string
        #gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

        # Rescale boxes from img_size to im0 size
        #det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

        # Print results
        #for c in det[:, -1].unique():
        #    n = (det[:, -1] == c).sum()  # detections per class
        #    s += f'{n} {names[int(c)]}s, '  # add to string

        # Write results
        res = []
        im0 = cv2.imread(str(img))
        for *xywh, conf, cls in reversed(pred): # xyxy correspond aux coordonnées des boites, conf correspond au score de la boite, cls l'indice du nom dans le dataset
            if xywh[0] <= 0.25 and xywh[1] <= 0.25:  #Haut gauche
                xywh.append(0)
            elif xywh[0] <= 0.75 and xywh[1] <= 0.25: #Haut
                xywh.append(1)
            elif xywh[1] <= 0.25: #Haut droite
                xywh.append(2)
            elif xywh[0] <= 0.25 and xywh[1] <= 0.75: #Gauche
                xywh.append(3)
            elif xywh[0] <= 0.75 and xywh[1] <= 0.75: #Milieu
                if xywh[0] <= 0.35: #Milieu gauche
                    xywh.append(4.1)
                elif xywh[0] >= 0.65: #Milieu droite
                    xywh.append(4.2)
                else:   #Milieu
                    xywh.append(4)
            elif xywh[1] <= 0.75: #Droite
                xywh.append(5)
            elif xywh[0] <= 0.25: #Bas gauche
                xywh.append(6)
            elif xywh[0] <= 0.75: #Bas
                xywh.append(7)
            else: # Bas droite
                xywh.append(8)

            res.append([xywh[0], xywh[1], xywh[2], xywh[3], xywh[4], conf, names[int(cls)]])
            # Compute the image
            height, width = im0.shape[0:2]
            # Convert coordinates to normalized corners
            xyxyn = torch.tensor([float(k) for k in xywh2xyxy(xywh)])
            # De-normalize the corners
            xyxy = [xyxyn[0] * width, xyxyn[1] * height,
                    xyxyn[2] * width, xyxyn[3] * height]
            # Make sure it's all a list of ints
            xyxy = list(map(int,xyxy))
            # Plot one box, inspired by plot_one_box
            # Line thickness, function of the size
            tl = round(0.002 * (im0.shape[0] + im0.shape[1]) / 2) + 1
            color = colors[int(cls)] # Colors
            # Define the two corners of the rectangle
            corner1 = (int(xyxy[0]), int(xyxy[1]))
            corner2 = (int(xyxy[2]), int(xyxy[3]))
            im0 = cv2.rectangle(im0, corner1, corner2, color, tl, cv2.LINE_AA)
            # Now add the label
            label = f"{names[int(cls)]} {conf:.2f}"
            label_tf = max(tl - 1, 1) # Font thickness for label
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3,
                    thickness=label_tf)[0]
            corner2 = corner1[0] + t_size[0], corner1[1] - t_size[1] - 3
            # Underlying rectangle
            im0 = cv2.rectangle(im0, corner1, corner2, color, -1, cv2.LINE_AA)
            # And now the text
            im0 = cv2.putText(im0, label, (corner1[0], corner1[1]-2),
                    0, tl / 3, [255, 255, 255], thickness=label_tf,
                    lineType=cv2.LINE_AA)

        print(f"Writing new image to {img}")
        cv2.imwrite(str(img), im0)

        situation = {
            0: "in the top left-hand corner.",
            1: "on the top",
            2: "in the top right-hand corner.",
            3: "on the left.",
            4: "right in front of you.",
            5: "on the right.",
            6: "in the bottom left-hand corner.",
            7: "at the bottom.",
            8: "in the bottom right-hand corner."
        }

        for loc in range(9):
            objects = {}
            match = [x for x in res if math.floor(x[4]) == loc]
            for x in match:
                if x[6] not in objects:
                    objects[x[6]] = 1
                else:
                    objects[x[6]] += 1
            if len(objects) == 1:
                item = next(iter(objects))
                description += f'There is {objects[item]} {item} {situation[loc]} '
            elif len(objects) > 1:
                objects = dict(sorted(objects.items(), key=lambda item: item[1], reverse=True))
                keylist = list(objects.keys())
                text = ""
                for obj in keylist[:-2]:
                    text += f'{objects[obj]} {obj}, '
                description += f'There are {text}{objects[keylist[-2]]} {keylist[-2]} and {objects[keylist[-1]]} {keylist[-1]} {situation[loc]} '

        return description
