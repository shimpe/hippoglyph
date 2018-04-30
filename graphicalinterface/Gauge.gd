extends Node2D

# class member variables go here, for example:
# var a = 2
# var b = "textvar"

func _ready():
	# Called when the node is added to the scene for the first time.
	# Initialization here
	pass
	
func set_value(val):
	var scaledval = val*90*PI/180 # val between -1, 1 beomes value between -pi/2 and pi/2
	get_node("Gauge/Pointer").rotation = scaledval
#func _process(delta):
#	# Called every frame. Delta is time since last frame.
#	# Update game logic here.
#	pass
