if (! Detector.webgl) Detector.addGetWebGLMessage();

var container, stats;
var camera, scene, renderer;
var light;
var mouseX = 0, mouseY = 0;
var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;
var fieldOfView = 45;
var drawDistance = 500;
var skyColour = 0x6FAEDC;
var fogDistance = 0.007000;

$(function() {
	init();
	animate();
});

function addObjectFromFile(file, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, LOD)
{
	// Example of a cube
	
	var loader = new THREE.JSONLoader();
    loader.load(file, function(geometry)
    {
		var material = new THREE.MeshLambertMaterial({color: 0x55B663});
		mesh = new THREE.Mesh(geometry, material);
		mesh.position.x = PosX;
		mesh.position.y = PosY;
		mesh.position.z = PosZ;
		mesh.rotation.x = RotX;
		mesh.rotation.y = RotY;
		mesh.rotation.z = RotZ;
		mesh.rotation.w = RotW;
		scene.addObject(mesh);
    });
}

function addInst(ID, ModelName, Interior, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, LOD)
{
	// Example of a cube
	var object = new THREE.Mesh(new THREE.BoxGeometry(10, 10, 10), new THREE.MeshNormalMaterial());
	
	object.position.x = PosX;
	object.position.y = PosY;
	object.position.z = PosZ;
	object.rotation.x = RotX;
	object.rotation.y = RotY;
	object.rotation.z = RotZ;
	object.rotation.w = RotW;
	return object;
}

var controls;

function init()
{

	container = document.getElementById('container');

	camera = new THREE.PerspectiveCamera(fieldOfView, window.innerWidth/window.innerHeight, 0.1, drawDistance);
	camera.position.x = 1893;
	camera.position.y = 1967;
	camera.position.z = 100;
	
	camera.up = THREE.Vector3(0,0,1);
	controls = new THREE.FlyControls( camera );
	controls.movementSpeed = 5000;
	controls.domElement = container;
	controls.rollSpeed = Math.PI / 500;
	controls.autoForward = false;
	controls.dragToLook = true;


	scene = new THREE.Scene();

	// Add fog
	
	scene.fog = new THREE.FogExp2(skyColour,fogDistance);

	light = new THREE.DirectionalLight(0xffffff);
	light.position.set(0, 0, 1).normalize();
	scene.add(light);



	// Add objects from file(s)
	/*var json = '[{"file": "objects/arrowhead.js", "PosX": -10 ,"PosY": 0,"PosZ": 0,"RotX": 45,"RotY": 45, "RotZ": 45,"RotW": 45 ,"LOD": 1},' + 
'{"file": "objects/arrowhead.js", "PosX": 0 ,"PosY": 0,"PosZ": 0,"RotX": 45,"RotY": 45, "RotZ": 45,"RotW": 45 ,"LOD": 1}]';
	json = JSON.parse(json);
	json.forEach(function(obj) {
		scene.add(addObjectFromFile(obj.file,obj.PosX, obj.PosY, obj.PosZ, obj.RotX, obj.RotY, obj.RotZ, obj.RotW, obj.LOD));
	});*/
	
	/*
	var loader = new THREE.ObjectLoader();
	loader.load("objects/coach.js", function(obj){
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	*/
	var loader = new THREE.ObjectLoader();
	/*
	loader.load("objects/donuts_sfw.js", function(obj){
		obj.position.y = 10;
		obj.position.x = 10;
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	*/
	/*
	loader.load("objects/donuts_sfw.js", function(obj){
		obj.position.y = 5;
		obj.position.x = 5;
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	
	loader.load("objects/lake_sfw.js", function(obj){
		obj.position.y = -5;
		obj.position.x = -5;
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	
	loader.load("objects/coach.js", function(obj){
		obj.position.y = -10;
		obj.position.x = -10;
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	
	loader.load("objects/coach.js", function(obj){
		obj.position.y = -15;
		obj.position.x = -15;
		obj.rotation.x = 0;
		obj.rotation.y = 0;
		obj.rotation.x = 0;
		scene.add(obj);
	});
	*/
	
	//scene.add(addInst(1, "box", "interior", 0, 0, 0, 45, 45, 45, 45, -1));
	
	//scene.add(addObjectFromFile('objects/arrowhead.js',-10, 0, 0, 45, 45, 45, 45, -1));

	renderer = new THREE.WebGLRenderer({ antialias: false });	// Turn antialias off for now
	renderer.setSize(window.innerWidth, window.innerHeight);

	// Set colour of sky
	renderer.setClearColor(skyColour);

	container.appendChild(renderer.domElement);

	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	container.appendChild(stats.domElement);

	document.addEventListener('mousemove', onDocumentMouseMove, false);

	window.addEventListener('resize', onWindowResize, false);
	
	$.getJSON("IPL.js", function(data) {
		var j = 0;
		for (var i in data)
		{
			var item = data[i];
			if (item.LOD == -1) {
				var callback = (function(item){
					return function(obj){
						scene.add(obj);
						
						obj.position.x = item.PosX;
						obj.position.y = item.PosY;
						obj.position.z = item.PosZ;
						
						/*obj.rotation.x = item.RotX;
						obj.rotation.y = item.RotY;
						obj.rotation.z = item.RotZ;*/
						
						//obj.rotation.setFromQuaternion(new THREE.Quaternion(item.RotX, item.RotY, item.RotZ, item.RotW));
						//obj.useQuaternion = true;
						/*obj.quaternion.x = item.RotX;
						obj.quaternion.y = item.RotY;
						obj.quaternion.z = item.RotZ;
						obj.quaternion.w = item.RotW;*/
						
						
						obj.up = THREE.Vector3(0,0,1);
						//console.log(item);
						//console.log(obj);
					}
				}
				)(item);
				
				loader.load("models/"+item["ModelName"]+".js", callback);
				/*j ++;
				if (j > 5)
					break;*/
			}
		}
	});
	
	// Set camera to pretty area
	
	camera.position.x = 1479.63909229102;
	camera.position.y = 2473.2470252524013;
	camera.position.z = 15.388867040383882;
	
	camera.rotation.x = -1.5828726737676089;
	camera.rotation.y = -0.4596641624974161;
	camera.rotation.z = -3.118131702706542;
}



function onWindowResize()
{

	windowHalfX = window.innerWidth / 2;
	windowHalfY = window.innerHeight / 2;
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth, window.innerHeight);
}

function onDocumentMouseMove(event)
{

	mouseX = (event.clientX - windowHalfX);
	mouseY = (event.clientY - windowHalfY);
}

function animate()
{

	requestAnimationFrame(animate);

	// Animation here

	render();
	stats.update();
}

function render()
{
	controls.movementSpeed = 0.33;
	controls.update(1);
	
	renderer.render(scene, camera);
}
