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
var fogDistance = 0.001000;

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
	camera.position.x = 2127;
	camera.position.y = 2453;
	camera.position.z = 10;
	
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

	/*light = new THREE.DirectionalLight(0xffffff);
	light.position.set(0, 0, 1).normalize();*/
	light = new THREE.AmbientLight(0xFFFFFF);
	scene.add(light);



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
	
	var loader = new THREE.ObjectLoader();
	var mloader = new THREE.Loader();
	loader.texturePath = "./";
	$.getJSON("data/positions.json", function(data) {
		var j = 0;
		for (var i in data)
		{
			var item = data[i];
			if (item.LOD == -1) {
				var callback = (function(item){
					return function(json){
						obj = loader.parse(json)
						
						/*mats = obj["materials"][0];
						for (var i in mats) {
							jmat = mats[i];
							tmat = obj.material.materials[i];
							//		function create_texture( where, name, sourceFile, repeat, offset, wrap, anisotropy ) {
							//create_texture( mpars, 'map', m.mapDiffuse, m.mapDiffuseRepeat, m.mapDiffuseOffset, m.mapDiffuseWrap, m.mapDiffuseAnisotropy );
							loader.create_texture(tmat, 'map', undefined, undefined, 
						}*/
						
						var m = mloader.initMaterials(json.materials[0].materials, "./");
						for (mat_i in m) {
							mat = m[mat_i]
							map = mat.mat
							if (map) {
								map.wrapS = THREE.RepeatWrapping
								map.wrapT = THREE.RepeatWrapping
								map.magFilter = THREE.NearestFilter
							}
						}
						obj.material = new THREE.MeshFaceMaterial(m);
						
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
						console.log(obj);
					}
				}
				)(item);
				
				$.getJSON("data/models/"+item["ModelName"]+".js", callback)
				//loader.load("data/models/"+item["ModelName"]+".js", callback);
				/*j ++;
				if (j > 5)
					break;*/
			}
		}
	});
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
