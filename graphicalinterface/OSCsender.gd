extends OSCsender

var parent = null
var passedbyzero = false

func _process(delta):
	if (parent == null):
		return
	var anim = parent.get_node("plate0/AnimationPlayer")
	if (anim && anim.playback_active && anim.current_animation_position < 1 && passedbyzero == false):
		msg_address("/godot/clockplate" )
		msg_add_string("minute")
		msg_send()
		passedbyzero = true
	elif (anim.current_animation_position >= 1 && passedbyzero == true):
		passedbyzero = false
	

func _ready():
	passedbyzero = false
	set_process(true)
