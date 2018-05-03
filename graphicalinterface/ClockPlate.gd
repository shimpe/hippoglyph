extends Node2D

# class member variables go here, for example:
# var a = 2
# var b = "textvar"
var nodes = ["do", "dosharp", "re", "resharp", "mi", "fa", "fasharp", "sol", "solsharp", "la", "lasharp", "si"]

func clip_value(value, minimum, maximum):
	if minimum > maximum:
		var temp = minimum
		minimum = maximum
		maximum = temp
	if value < minimum:
		return minimum
	elif value > maximum:
		return maximum
	else:
		return value

func linlin(value, in_min, in_max, out_min, out_max, clip):
	if in_min == in_max:
		if value == in_min and out_min == out_max:
			return out_min
		return 0

	var output = ((out_min + out_max) + (out_max - out_min) * (
              (2 * value - (in_min + in_max)) / float(in_max - in_min))) / 2.0
	if clip:
		output = clip_value(output, out_min, out_max)
		
	return output


func on_osc(msg):
	if (msg.empty()):
		return
	if (msg.address() == "/sc/note"):
		var note = msg.arg(0)
		var dur = 1
		if (msg.arg_num() > 1):
		    dur = msg.arg(1)
		#print("note: ", note, "dur: ", dur);
		var expl = get_node(nodes[note]).find_node("Explosion")
		if (expl.is_playing()):
			expl.stop();
			expl.frame = 0
		#var newspeed = 25/dur;
		#if dur != 0:
		#	print("dur: ", dur)
		#	expl.frames.set_animation_speed("default", newspeed)
		#else:
		#	expl.frames.set_animation_speed("default", 1)
		expl.play()
	if (msg.address() == "/mindwave/raw"):
		var value = msg.arg(0)
		get_node("MultiBar").set_value(value)
	if (msg.address() == "/mindwave/attention"):
		var value = msg.arg(0)
		var mappedvalue = linlin(value,0,100,-1,1,true)
		get_node("Aandacht").set_value(mappedvalue)
	if (msg.address() == "/mindwave/meditation"):
		var value = msg.arg(0)
		var mappedvalue = linlin(value,0,100,-1,1,true)
		get_node("Meditatie").set_value(mappedvalue)
	#if (msg.address() == "/mindwave/resetbrain"):
	#	for i in range(100):
	#		get_node("MultiBar").set_value(0)
	#	get_node("Aandacht").set_value(0)
	#	get_node("Meditatie"). set_value(0)

func _ready():
	# Called when the node is added to the scene for the first time.
	# Initialization here
	var R = 230
	var pi = 3.1415
	var alpha = 90 * pi/180.0
	var offsX = 512
	var offsY = 300
	var red = Color(1,0,0,1)
	var white = Color(1,1,1,1)
	var i = 0
	for n in nodes:
		get_node(n).translate(Vector2(offsX+R*cos(alpha), offsY-R*sin(alpha)))
		get_node(n).modulate = red.linear_interpolate(white, i/12.0)
		alpha = alpha - 30*pi/180.0
		i =  i+1
		#get_node(n).find_node("Explosion").play();
	find_node("OSCsender").parent = self
	
	
#func _process(delta):
#	# Called every frame. Delta is time since last frame.
#	# Update game logic here.	
#	pass
