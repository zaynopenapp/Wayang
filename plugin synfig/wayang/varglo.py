# Synfig plugin: Wayang/Shapekey/Controller
# Helps controller shape/animated node
# (c) 2025/2026 ABIDIN IDN

namafile = 'awal1.sif'
jenis_ik = None
bone_ik = ''
guid_flip = None

fps = 25
root_file = None
sudut_max = None
sudut_min = None
sudutik_to_target = 0 #khusus ik smartkey
mode_smartkey = None #mode baru dengan cara mencari negatif animation
mode_before = None
input_areatime = -120
edit_areatime = -120
length_time = 50 #max 99
jump = 10
time_left = -4.8
time_right = -2.8
time_base = -2 # for base shape. if change all key must change too
influence = None

id = None # guid for bone controller 
id_edit_sub_smartkey = None

el_controller_bone = None   # untuk real time controller sudut
el_animasi_controller_bone = None# untuk data min max berasal dari sudut
main_template = None
el_angle_IK = None
el_influence = None

ada_freetime = False
hook = False  # if you need hook set to True
ik_smartkey = False
vectorangle = False
modul_GTK = True
developer = True
undo = False
synfig_above_154= True
delete_shapekey = False

controller_data = [] # command injection list
list_layers = []
controller = 0 #count controller
valueattime_elcounter = 0
mode = ['play','editmode']
nama_controller = 'none'
id_controller = 'none'
smartkey_list = []
skeleton_list = []
shapekey_rename_list = []
undo_list = ['undo_1']
valueattime_list = []
file_undo = None
data_error = {}
raw_file = None
found_keys = 0
list_skeleton = []
list_hook = []
el_pos_controller = None
list_guid_inf = []
guid_clone_inf = {}
type_controller = ''
bone_cont_layer = None
el_name_bone = None
el_name_current_cont = None
user_animated_target = None
hook_idx = 0

#clone
clone_layergroup = 'none'
groupclone = None
list_new_bone={}
list_guid_umum = {}
list_guid_bone = {}
root_bone_guid = None
total_controller = 0
clone_guid = None
name_clone_shapekey = ''
