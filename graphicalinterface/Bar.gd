extends ColorRect

# class member variables go here, for example:
var kleur = Color(1, 1, 1, 0.5)
var scale = 1

func _ready():
	# Called when the node is added to the scene for the first time.
	# Initialization here
	set_value(0)
	
func set_value(val):
	var mostneg = Color(1,0,0,1)
	var zero = Color(1,1,0,1)
	var mostpos = Color(0,1,1,1)
	if ((-1 < val) && (val <= 0)):
		color = zero.linear_interpolate(mostneg, abs(val))
	else:
		color = zero.linear_interpolate(mostpos, val)
	var oldscale = get_scale();
	get_parent().set_scale(Vector2(oldscale.x, -val*scale))

#func _process(delta):
#	# Called every frame. Delta is time since last frame.
#	# Update game logic here.
#	pass
