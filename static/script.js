// author:  Cristian Salazar (christiansalazarh@gmail.com) www.chileshift.cl
// https://www.npmjs.com/package/parse-multipart
function MultiPart_getBoundary(header) {
	var items = header.split(';');
	if(items)
		for(i=0;i<items.length;i++){
			var item = (new String(items[i])).trim();
			if(item.indexOf('boundary') >= 0){
				var k = item.split('=');
				return (new String(k[1])).trim();
			}
		}
	return "";
}

// Copyright@ 2013-2014 Wolfgang Kuehn, released under the MIT license.
// https://gist.github.com/woffleloffle/5223f25713b376bb6700c90772ac41ec
function MultiPart_parse(body, boundary) {
	/*var m = contentType.match(/boundary=(?:"([^"]+)"|([^;]+))/i);
	if (!m) { throw new Error('Bad content-type header, no multipart boundary'); }
	let s, fieldName;
	let boundary = m[1] || m[2];*/

	function Header_parse(header) {
		var headerFields = {};
		var matchResult = header.match(/^.*name="([^"]*)"$/);
		if (matchResult) headerFields.name = matchResult[1];
		return headerFields;
	}

	function rawStringToBuffer(str) {
		var idx, len = str.length,
		arr = new Array(len);
		for (idx = 0; idx < len; ++idx) {
			arr[idx] = str.charCodeAt(idx) & 0xFF;
		}
		return new Uint8Array(arr).buffer;
	}

	// \r\n is part of the boundary.
	boundary = '\r\n--' + boundary;

	var isRaw = typeof(body) !== 'string';

	if (isRaw) {
		var view = new Uint8Array(body);
		s = String.fromCharCode.apply(null, view);
	} else {
		s = body;
	}

	// Prepend what has been stripped by the body parsing mechanism.
	s = '\r\n' + s;

	var parts = s.split(new RegExp(boundary)),
		partsByName = {};
		
	// First part is a preamble, last part is closing '--'
	for (var i = 1; i < parts.length - 1; i++) {
		var subparts = parts[i].split('\r\n\r\n');
		var headers = subparts[0].split('\r\n');
		for (var j = 1; j < headers.length; j++) {
			var headerFields = Header_parse(headers[j]);
			if (headerFields.name) {
				fieldName = headerFields.name;
			}
		}
		partsByName[fieldName] = isRaw ? rawStringToBuffer(subparts[1]) : subparts[1];
	}

	return partsByName;
}


// ==========================================================================================


// elements of the HTML page
var pictureSelect = document.getElementById('pictureSelect');
var preview = document.getElementById('preview');
var endpointRadios = document.getElementsByName('endpointRadio');
var checkbox = document.getElementById("check");
var button = document.getElementById('uploadButton');
var caption = document.getElementById('caption');
var resultImage = document.getElementById('boxes');


// loads an image from the computer (selected in the node passed as an argument)
// and displays it in the image of ID preview
function loadImageFromInput(node) {
	if(node.files.length > 0 && node.files[0].type.startsWith("image/")) {
		preview.src = URL.createObjectURL(node.files[0]);
		button.disabled = false;
	} else {
		button.disabled = true;
	}
}

// when the page is loaded, if an image is already 
// selected in pictureSelect, display it
loadImageFromInput(pictureSelect);

var loadImage = function(event) {
	loadImageFromInput(event.target)
};

// when the selected image changes, update the display
pictureSelect.addEventListener("change", loadImage);


// yields the value of the currently selected checkbox
function getEndpoint() {
	for(var i = 0; i < endpointRadios.length; i++) {
		if(endpointRadios[i].checked) {
			return endpointRadios[i].value;
		}
	}
}

// if the endpoint selected at page load is captionning, disable the checkbox
// we do this because the captionning cannot yield an image with boxes
// only the yolo-based model can do this
checkbox.disabled = (getEndpoint() === 'captioning');

// when a new endpoint is selected, enable or disable the checkbox
for(var i = 0; i < endpointRadios.length; i++) {
	endpointRadios[i].addEventListener('change', function(event) {
        checkbox.disabled = (event.target.value === 'captioning')
    });
}


// Converts a binary image (array of bytes) to an URL
// containing a base 64 representation of the image
function imgToUrl(img, imgType) {
	let buffer = new Uint8Array(img);
	let blob = new Blob([buffer], {type:imgType});
	let urlCreator = window.URL || window.webkitURL;
	return urlCreator.createObjectURL(blob);
}


// I blame backend for having to use this
function capitalizeFirstLetter(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}


// initialize the script at page load.
window.addEventListener('load', function () { 

	const file = {
		dom    : pictureSelect,
		binary : null
	};

	const reader = new FileReader(); // asynchronous file reader

	// when the file has been read, store the result
	reader.addEventListener("load", function () {
		file.binary = reader.result;
	});

	// if a file is already selected, read it
	if(file.dom.files[0]) {
		reader.readAsArrayBuffer(file.dom.files[0]);
	}

	// when the the user selects a new file, read it
	// if an image is already being read, abort the first reading
	file.dom.addEventListener("change", function() {
		if(reader.readyState === FileReader.LOADING) {
			reader.abort();
		}
		reader.readAsArrayBuffer(file.dom.files[0]);
	});

	// function that allows to send the multipart request
	// help from : https://developer.mozilla.org/fr/docs/Learn/Forms/Sending_forms_through_JavaScript
	function sendData() {
		// If there is a selected file, wait it is read
		// If there is not, delay the execution of the function
		if(!file.binary && file.dom.files.length > 0) {
			setTimeout(sendData, 10);
			return;
		}

		endpoint = '/' + getEndpoint(); // get the selected endpoint

		const XHR = new XMLHttpRequest(); // new request

		// We need a separator to define each part of the request
		const boundary = "blob";

		let data = []; // request body content
		
		// chechbox data (only if the endpoint is yolo)
		if(endpoint === '/yolo'){
			data.push("--" + boundary + "\r\n");
			data.push('content-disposition: form-data; name="' + checkbox.name + '"\r\n');
			data.push('\r\n');
			data.push(checkbox.checked + "\r\n"); // tells if the user required the result image to be sent back
		}
		
		// image data
		data.push("--" + boundary + "\r\n");
		data.push('content-disposition: form-data; name="' + file.dom.name + '"; filename="' + file.dom.files[0].name + '"\r\n');
		data.push('Content-Type: ' + file.dom.files[0].type + '\r\n'); // MIME type
		data.push('\r\n');
		data.push(file.binary);
		data.push('\r\n');

		data.push("--" + boundary + "--\r\n"); // Close the body's request

		// select the right endpoint depending on the user's inputs
		XHR.open('POST', endpoint);

		// add the required HTTP header to handle a multipart form data POST request
		XHR.setRequestHeader('Content-Type',"multipart/form-data; boundary=" + boundary);

		// when the response is recieved, insert the elements in the page
		XHR.onreadystatechange = function() { 
			if (XHR.readyState == 4 && XHR.status == 200) {
				let header = XHR.getResponseHeader('Content-Type');
				let boundary = MultiPart_getBoundary(header);
				let res = MultiPart_parse(XHR.response, boundary);
				if('caption' in res) {
					caption.textContent = capitalizeFirstLetter(new TextDecoder("utf-8").decode(res['caption']));
				}
				resultImage.src = ""
				for(key in res) {
					// the image name should be preview.png / preview.jpg / ...
					console.log(key);
					if(key.startsWith('preview.')) {
						resultImage.src = imgToUrl(res[key], "image/" + key.substring(8));;
						break;
					}
				}
			}
		}
		
		// we need this to prevent JavaScript from converting the image
		// in the response into a string
		XHR.responseType = "arraybuffer";

		// finally, we send the request
		XHR.send(new Blob(data));
	}
	
	// when the form is submitted, prevent the default request from being sent
	// instead, call sendData which will send our custom made request
	document.getElementById("captForm").addEventListener('submit', function(event) {
		event.preventDefault();
		sendData();
	});
});
