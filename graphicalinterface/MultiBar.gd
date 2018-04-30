extends Node2D

# class member variables go here, for example:
# var a = 2
# var b = "textvar"
var num = 80
var vals = []

# test code
#var prev_value = 0

func _ready():
	var scene = load("res://Bar.tscn")
	for i in range(num):
		var scene_instance = scene.instance()
		scene_instance.set_name("scene "+str(i))
		scene_instance.set_position(Vector2(i*1024/num, 0))
		vals.append(0);
		add_child(scene_instance)
	set_process(true)

func set_value(val):
	vals.pop_front()
	vals.push_back(val/255.0)

func _process(delta):
	var i = 0
	# test code
	# prev_value = prev_value + rand_range(-0.05,0.05)
	# set_value(prev_value)
	# set_value(prev_value)
	for v in vals:
		get_node("scene "+str(i)).find_node("Bar").set_value(v)
		i = i + 1
		