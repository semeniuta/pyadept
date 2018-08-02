// Grammar for Adept server commands

root ::= command_chain
command_chain ::= command+
command ::= motion_command | break_command | air_command | speed_command
speed_command ::= "set_speed" ":" digit
air_command ::= ('enable_air' | 'disable_air') delimiter
break_command ::= "break" delimiter
motion_command ::= motion_command_name ":" location delimiter
motion_command_name ::= "move_to" | "move_rel_world" | "move_rel_tool" | "move_joints" | "move_rel_joints"
location ::= real "," real "," real "," real "," real "," real
real ::= digit+ "." fractional;
fractional ::= digit digit digit
digit ::= [0-9]
delimiter ::= "\r\n"
