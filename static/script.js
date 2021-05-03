//author:  Cristian Salazar (christiansalazarh@gmail.com) www.chileshift.cl
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
var preview = document.getElementById('preview');
var caption = document.getElementById('caption');
var image = document.getElementById('boxes');
var button = document.getElementById('uploadButton');


var loadImageFromInput = function(node) {
	if(node.files.length > 0 && node.files[0].type.startsWith("image/")) {
		preview.src = URL.createObjectURL(node.files[0]);
		button.disabled = false;
	} else {
		button.disabled = true;
	}
}

loadImageFromInput(document.getElementById('pictureSelect'));

var loadImage = function(event) {
	loadImageFromInput(event.target)
};

//function hexToBase64(str) {
//    return btoa(String.fromCharCode.apply(null, str.replace(/\r|\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" ")));
//}

function imgToUrl(img, imgType) {
	let buffer = new Uint8Array(img);
	let blob = new Blob([buffer], {type:imgType});
	let urlCreator = window.URL || window.webkitURL;
	return urlCreator.createObjectURL(blob);
}


// initialize the script at page load.
window.addEventListener('load', function () { 

	const checkbox = document.getElementById("check");
	const file = {
		dom    : document.getElementById("pictureSelect"),
		binary : null
	};

	const reader = new FileReader(); // asynchronous file reader

	reader.addEventListener("load", function () { // when the file has been read, store the result
		file.binary = reader.result;
	});

	if(file.dom.files[0]) { // if a file is already selected, read it
		reader.readAsArrayBuffer(file.dom.files[0]);
	}

	file.dom.addEventListener("change", function() { // read a file the user selects it
		if(reader.readyState === FileReader.LOADING) { // if there is already a file being read, abort the reading procedure
			reader.abort();
		}
		reader.readAsArrayBuffer(file.dom.files[0]);
	});

	// function that allows to send the multipart request
	function sendData() {
		// If there is a selected file, wait it is read
		// If there is not, delay the execution of the function
		if(!file.binary && file.dom.files.length > 0) {
			setTimeout(sendData, 10);
			return;
		}

		const XHR = new XMLHttpRequest();

		// We need a separator to define each part of the request
		const boundary = "blob";

		let data = []; // request body content

		data.push("--" + boundary + "\r\n");
		data.push('content-disposition: form-data; name="' + checkbox.name + '"\r\n');
		data.push('\r\n');
		data.push(checkbox.checked + "\r\n"); // tells if the user required the result image to be sent back

		if (file.dom.files[0]) {
			data.push("--" + boundary + "\r\n");
			data.push('content-disposition: form-data; name="' + file.dom.name + '"; filename="' + file.dom.files[0].name + '"\r\n');
			data.push('Content-Type: ' + file.dom.files[0].type + '\r\n'); // MIME type
			data.push('\r\n');
			data.push(file.binary);
			data.push('\r\n');
		}

		data.push("--" + boundary + "--\r\n"); // Close the body's request

		XHR.open('POST', '/captionning');

		// Add the required HTTP header to handle a multipart form data POST request
		XHR.setRequestHeader('Content-Type',"multipart/form-data; boundary=" + boundary);

		XHR.onreadystatechange = function() { 
			if (XHR.readyState == 4 && XHR.status == 200) {
				let header = XHR.getResponseHeader('Content-Type');
				let boundary = MultiPart_getBoundary(header);
				let res = MultiPart_parse(XHR.response, boundary);
				if('caption' in res) {
					caption.textContent = new TextDecoder("utf-8").decode(res['caption']);
				}
				if('preview.jpg' in res) {
					image.src = "data:image/jpeg;base64," + imgToBase64(res['preview.jpg']);
				} else if ('preview.png' in res) {
					image.src = imgToUrl(res['preview.png'], "image/png");
				} else {
					image.src = ""
				}
			}
		}
		
		XHR.responseType = "arraybuffer";

		XHR.send(new Blob(data));
	}

	document.getElementById("captForm").addEventListener('submit', function(event) {
		event.preventDefault();
		sendData();
	});
});
