# Synfig plugin: Shapekey(Wayang)
# Helps controller shape/animated node
# (c) 2025/2026 ABIDIN IDN

import uuid
import xml.etree.ElementTree as ET
import copy
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pkgutil
import math
import random
import re
import varglo
import errno

from colorprint import bcolors

def get_selisih_time():

	idx_time = -2 #target pasti di index time -2 atau pindahkan ke -180 f/ -7.2 <> -5.2
	time_minimal = (idx_time-1) * (varglo.length_time+varglo.jump)/varglo.fps;
	return round((time_minimal-varglo.time_left),3)

def load_template(kunci_tag):
	
	el_temp = varglo.main_template.find(kunci_tag)
	return copy.deepcopy(el_temp)

def replace(parent, el_new):

	parent.remove(parent[0])
	parent.append(el_new)

def ganti_nama_layer(el_layer_bone):

	if 'desc' in el_layer_bone[0].attrib:
		el_layer_bone[0].set('desc','New Controller')

def cari_skeleton():

	varglo.skeleton_list = []
	list_skeleton = varglo.root_file.findall(".//*[@type='skeleton']")

	idx = 1
	for layer in list_skeleton:
		desc = "skeleton"
		if 'desc' in layer.attrib:
			desc = layer.get('desc')
		varglo.skeleton_list.append(['skeleton_'+str(idx),desc,layer])
		idx +=1

def merge_skeletons(jenis):

	el_parentlist_entry = jenis[0].find(".//static_list")

	for el in jenis:
		if not el == jenis[0]:
			for el_entry in el.findall(".//entry"):
				el_parentlist_entry.append(el_entry)

			el.set('rinjani','NTB')
			el_p = varglo.root_file.find(".//*[@rinjani='NTB']/../..")

			if el_p == None:
				varglo.root_file.remove(el)

			else:
				el_p[0].remove(el)

	print("Merge skeletons Done!")

def set_static_bones():

	el_bones = varglo.root_file.find(".//bones")

	for bone in el_bones.findall(".//bone"):
		set_static_bone(bone, "bone")

def masukan_templateIK(bone_path,bone_layer_path):

	def isi_guidbaru(el_guid,data_guid,guid_root):

		if el_guid.get('guid') == guid_root:
			return

		if not el_guid.get('guid') in data_guid:
			new_guid = str(uuid.uuid4())
			data_guid[el_guid.get('guid')]=new_guid
			el_guid.set('guid',new_guid)

		else:
			el_guid.set('guid',data_guid[el_guid.get('guid')])
			
	el_bones_baru = load_template(bone_path)

	el_layer_bone = load_template(bone_layer_path)
	ganti_nama_layer(el_layer_bone)

	el_bones = varglo.root_file.find(".//bones") # cari ada bone awal

	if el_bones:
		el_root = el_bones.find(".//bone_root")
		guid_root = el_root.get('guid')

		for el_this in el_bones_baru.findall(".//*[@guid='SK2_LINKTONEWPARENT']"):
			el_this.set('guid',guid_root)

		data_guid = {}
		for el_guid in el_bones_baru.findall(".//*[@guid]"):
			isi_guidbaru(el_guid,data_guid,guid_root)

		for el_guid in el_layer_bone.findall(".//*[@guid]"):
			isi_guidbaru(el_guid,data_guid,guid_root)

		varglo.root_file.append(el_layer_bone[0])

		for el_bone in el_bones_baru.findall(".//bone[@type='bone_object']"):
			el_bones.append(el_bone)

	else:

		el_root = el_bones_baru.find(".//bone_root")
		guid_root = el_root.get('guid')

		for el_this in el_bones_baru.findall(".//*[@guid='SK2_LINKTONEWPARENT']"):
			el_this.set('guid',guid_root)
		#buat guid baru agar tidak konplik guid
		data_guid = {}
		for el_guid in el_bones_baru.findall(".//*[@guid]"):
			isi_guidbaru(el_guid,data_guid,guid_root)
			
		for el_guid in el_layer_bone.findall(".//*[@guid]"):
			isi_guidbaru(el_guid,data_guid,guid_root)
		# masukan layer bones ke file
		varglo.root_file.append(el_bones_baru[0])
		varglo.root_file.append(el_layer_bone[0])

	set_static_bones()

def masukan_templateSK():

	el_bones = varglo.root_file.find(".//bones") # cari ada bone awal
	el_layer_bone = load_template(".//*[@kunci='SK2_layerbonesm']")
	el_bones_baru = load_template(".//*[@kunci='SK2_bonesk']")

	ganti_nama_layer(el_layer_bone)

	def ganti_sudutminmax(el_bones_baru):
		#for min
		for el_this in el_bones_baru.findall(".//*[@value='SK2_sudut_min']"):
			el_this.set('value',str(varglo.sudut_min))
		#for max
		for el_this in el_bones_baru.findall(".//*[@value='SK2_sudut_max']"):
			el_this.set('value',str(varglo.sudut_max))

	if el_bones:
		el_root = el_bones.find(".//bone_root")
		guid_root = el_root.get('guid')
		
		el_bone = el_bones_baru.find(".//bone")
		new_guid = str(uuid.uuid4())
		el_bone.set('guid',new_guid)

		for el_this in el_bones_baru.findall(".//*[@guid='SK2_linktoboneroot']"):
			el_this.set('guid',guid_root)

		el_entrybone = el_layer_bone.find(".//*[@guid='SK2_linkguid']")
		el_entrybone.set('guid',new_guid)
		ganti_sudutminmax(el_bones_baru)
		el_bones.append(el_bone)
		varglo.root_file.append(el_layer_bone[0])

	else:
		#el_bones_baru = load_template(".//*[@kunci='SK2_bonesk']")
		el_root = el_bones_baru.find(".//bone_root")
		new_guidroot = str(uuid.uuid4())
		el_root.set('guid',new_guidroot)

		for el_this in el_bones_baru.findall(".//*[@guid='SK2_linktoboneroot']"):
			el_this.set('guid',new_guidroot)

		el_bone = el_bones_baru.find(".//bone")
		new_guidbone = str(uuid.uuid4())
		el_bone.set('guid',new_guidbone)
		el_entrybone = el_layer_bone.find(".//*[@guid='SK2_linkguid']")
		el_entrybone.set('guid',new_guidbone)
		ganti_sudutminmax(el_bones_baru)
		varglo.root_file.append(el_bones_baru[0])
		varglo.root_file.append(el_layer_bone[0])

def fileundo_load(jenis):
	
	varglo.root_file = varglo.file_undo
	print("    Undo plugin done!")

def cari_clone_data():

	print('[.] searching group clone shapekey')

	varglo.clone_layergroup = 'none'
	list_new_el_bone = []
	ditemukan = False
	copy_group = None
	list_new_el_bone_baru = {}

	for group in varglo.root_file.findall(".//*[@type='group']"):
		if 'desc' in group.attrib:
			data = group.get('desc')

			if '>' in data:
				varglo.clone_layergroup = data
				varglo.groupclone = group
				break

def ganti_guidnya(el):

	def umum(el_berguid):
		guid_apa = el_berguid.get('guid')
		
		if guid_apa in varglo.list_guid_umum:
			guid_b = varglo.list_guid_umum[guid_apa]
			el_berguid.set('guid',guid_b)

			if guid_apa in varglo.list_guid_inf: # in list guid inf or name SK
				varglo.guid_clone_inf[guid_apa]=guid_b
				#print("guid baru ",guid_b,guid_apa)

		else:
			guid_baru = str(uuid.uuid4())
			varglo.list_guid_umum[guid_apa]=guid_baru
			el_berguid.set('guid',guid_baru)

	for el_berguid in el.findall(".//*[@guid]"):

		if 'type' in el_berguid.attrib:
			if el_berguid.get('type')=='bone_object':# +++
				guid_apa = el_berguid.get('guid')
				
				if guid_apa != varglo.root_bone_guid : # abaikan jika guid itu sebuah root guid
					if guid_apa in varglo.list_new_bone:
						bone_cari = varglo.list_new_bone[guid_apa]
						guidnya = bone_cari.get('guid')
						el_berguid.set('guid',guidnya)

			else:
				umum(el_berguid)
			
		else:
			umum(el_berguid)

def get_guid_inf(bone):

	list_inf = bone.findall(".//scalex//entry/real")

	for el in list_inf:
		guid_this = el.get('guid')

		if not guid_this in varglo.list_guid_inf:
			varglo.list_guid_inf.append(guid_this)

	

def buat_bone_baru(copy_group):

	bones = varglo.root_file.find(".//bones")
	root_bone = varglo.root_file.find(".//bone_root")
	guit_rootbone = root_bone.get('guid')
	varglo.root_bone_guid = guit_rootbone

	for sk in copy_group.findall(".//*[@type='skeleton']"):
		for bone in sk.findall(".//bone"):
			guid_bone = bone.get('guid')

			bone_asli = bones.find(".//*/[@guid='{no}']".format(no= guid_bone))
			bone_copy = copy.deepcopy(bone_asli)
			guid_asli = bone_copy.get('guid')

			if not guid_asli in varglo.list_new_bone:
				guid_baru = str(uuid.uuid4())
				bone_copy.set('guid',guid_baru)
				varglo.list_new_bone[guid_asli]=bone_copy
	#ganti semua guid masing2 bone dan simpan guid barunya
	for newbone in varglo.list_new_bone:
		bone = varglo.list_new_bone[newbone]

		get_guid_inf(bone)
		ganti_guidnya(bone)

def append_list_shapekeys(bone,copy_group):

	parent_bone_cont= get_parent(bone,5)

	el_canvas = group_keys.find(".//param/canvas")
	text_layer = load_template(".//*[@kunci='SK_text_shapekeys']")
	el_string = text_layer.find(".//param/string")

	el_originbone = bone.find(".//origin/")

	for guid in varglo.list_guid_inf:
		for el_text in varglo.root_file.findall(".//*[@type='text']"):
			el_text_c = copy.deepcopy(el_text)
			el_this = el_text_c.find(".//link_on/average/entry/real")
			if guid == el_this.get('guid'):
				el_origin_text = el_text_c.find(".//param/add/rhs")
				replace(el_origin_text,el_originbone)
				el_canvas.append(el_text_c)

	if not group_ready:
		el_canvas_parent = copy_group.find(".//param/canvas")
		el_canvas_parent.append(group_keys)

def set_create_layer_skname(list_name_SK,el_nama_new,guid_this):

	for layer_text in list_name_SK:
		el_inf = layer_text.find('.//param/switch//link_on/average/entry')

		if not el_inf == None:
			guid_text_inf = el_inf[0].get("guid")
			if guid_text_inf == guid_this:

				el_name_text = layer_text.find(".//param/string/..")
				replace(el_name_text,el_nama_new)

def masukan_bonebaru(copy_group):

	print('[.] create bone')

	bones = varglo.root_file.find(".//bones")
	list_bone = []
	list_name_SK = copy_group.findall(".//*[@group='name_SK']")

	for newbone in varglo.list_new_bone:
		bone = varglo.list_new_bone[newbone]

		entry_namesk = bone.findall(".//name/join//dynamic_list/entry")

		for sk_name in entry_namesk:
			el_string = sk_name.find(".//link_off/string")
			#name = el_string.text
			el_string.text = varglo.name_clone_shapekey
			el_inf = sk_name.find(".//link_on/realstring/real/")
			guid_this_inf = el_inf.get('guid')

			set_create_layer_skname(list_name_SK,el_string,guid_this_inf)

		list_bone.append(bone)

	varglo.total_controller = len(list_bone)
	list_bone.reverse()

	if varglo.total_controller == 0:
		print("!!! missing bone")

	for bone in list_bone:
		bones.append(bone)

	print('[..] create bone done')

def set_new_namelayerbone_cont(copy_group,total_cont):

	bones = varglo.root_file.find(".//bones")
	root_bone = varglo.root_file.find(".//bone_root")
	guit_rootbone = root_bone.get('guid')
	varglo.root_bone_guid = guit_rootbone

	#for sk in copy_group.findall(".//*[@type='skeleton']"):
		#nama_layer = sk.get('desc')
		#pos = nama_layer.find("r_")
		#angka_cont = nama_layer[pos+2:]
		#val_add = int(angka_cont)+total_cont
		#sk.set('desc','Bone_controller_'+str(val_add))

def set_id_shapekey(el_link,id_shapekey):

	el_id_shapekey = el_link.find(".//timeloop/link_time//link/map_range/link/")
	guid_this = str(uuid.uuid4()) # guid 
	el_id_shapekey.set('guid',guid_this)

def set_new_shapekey(copy_group):

	print('[.] create all new value at layer')
	code = 0
	#total_cont = varglo.root_file.find(".//*[@name='smartkey_tcont']") #for valueattime
	total_cont = varglo.root_file.find(".//*[@name='shapekey_count']") # for manual range 
	if total_cont== None:
		code = 1
		print('!!! smartkey_tcont mising')
	else:
		code = int(float(total_cont.get('content')))

	list_id_SK = []
	nama = 'none'

	idx = 0

	for el_entry in copy_group.findall(".//timeloop/.."):
		id_shapekey = get_id_shapekey(el_entry)

		if not id_shapekey in list_id_SK:
			list_id_SK.append(id_shapekey)

	total = len(list_id_SK)

	if  total_cont != None:
		total_cont.set('content',str(total+code)) # update data shape key 
	
	set_new_namelayerbone_cont(copy_group,total)

def update_shapekey_count(list_shapekey):
	
	total_shapekey_notaktif = len(list_shapekey)

	total_cont = varglo.root_file.find(".//*[@name='shapekey_count']") # tanpa value attime
	if total_cont== None:
		cont = 1
		add_metamenu('shapekey_count','1')
		print("create_shapekey_count")
		
	else:
		cont = int(float(total_cont.get('content')))
		cont -= total_shapekey_notaktif
		total_cont.set('content',str(cont))

def erase_shapekey(): # cek shapekey apakah terkonek dengan controller di dalam group > copy

	bones = varglo.root_file.find(".//bones")

	list_shapekey = []
	for el_entry in copy_group.findall(".//timeloop/.."):
		id_shapekey = get_id_shapekey(el_entry)
		el_maprange = el_entry.find('.//map_range/..')

		if el_maprange == None:
			print("not synfig 2025!! map range not ready!!")

		else:
			el_link_controller = el_maprange.find('.//to_max/map_range/link/')
			ada_controller = False

			if not el_link_controller.tag == 'vectorlength':
				guid_controller = el_link_controller.get('guid')
				value_controller = el_link_controller.get('value')
				
				for bone in bones.findall('.//bone'):
					angle_bone = bone.find('.//angle/fromreal/link/real')

					if not angle_bone == None:
						if angle_bone.get('guid') == guid_controller:
							ada_controller = True
					else:
						continue

			else:
				el_target = el_link_controller.find(".//subtract/lhs/add")
				guid_controller = el_target.get("guid")

				for bone in bones.findall('.//bone'): # for IK converter/ik manual
					origin_bone = bone.find('.//origin/add/..')
					if origin_bone != None:
						if origin_bone[0].get('guid') == guid_controller:
							ada_controller = True

					else:
						continue

			if not ada_controller:
				if not id_shapekey in list_shapekey:
					list_shapekey.append(id_shapekey)
					print("!!! missing controller !!! ",id_shapekey)
				
				el_entry_parent= get_parent(el_entry,3)
				
				el_scalar = el_entry_parent.find('.//scalar/real')
				skala = int(float(el_scalar.get('value')))
				
				if skala == 1:
					el_entry_parent2 = get_parent(el_entry_parent,3)
					el_dasar = el_entry_parent2.find('.//add/lhs/add/rhs/')

					if 'guid' in el_dasar.attrib:
						el_dasar.attrib.pop('guid')

					el_dasar_c = copy.deepcopy(el_dasar)
					replace(el_entry_parent2,el_dasar_c)

				else:
					skala -= 1
					el_scalar.set('value',str(skala))
					el_entry_parent[0][0].remove(el_entry) # hapus entry yg tidak kontrollernya

	update_shapekey_count(list_shapekey)

def make_guid_clone(bone):

	el_this = bone.find(".//scalelx/switch/..")
	varglo.clone_guid = str(uuid.uuid4())

	if el_this[0].tag == 'switch':
		el_on = el_this.find(".//link_on/")
		el_on.set('guid',varglo.clone_guid)

	else:
		el_switch = load_template(".//*[@kunci='SK_clone']")
		el_guid = el_switch.find(".//link_on/")
		el_guid.set('guid',varglo.clone_guid)
		replace(el_this,el_switch[0])

def cek_jeniscont(layer):

	bones = varglo.root_file.find(".//bones")
	layer_bones = bones.findall(".//bone")

	for bone in layer.findall(".//bone"):
		guid_this = bone.get('guid')

		for bone in layer_bones:
			if guid_this == bone.get("guid"):
				name = bone.find(".//name/string")
				if name != None:
					if "shapekey" in name.text:
						make_guid_clone(bone)

def clone_shapekey():

	data = varglo.clone_layergroup
	group = varglo.groupclone
	#add desc
	pos = data.find(">")
	base_name = data[:pos]
	varglo.name_clone_shapekey = data[pos+1:] #get name new clone shapekey
	group.set('desc',base_name)
	copy_group = copy.deepcopy(group)
	copy_group.set('desc',base_name+'_clone')

	# MOVE OFFSET GROUP
	el_pos = copy_group.find('.//offset/vector') 
	x_pos = float(el_pos[0].text)
	y_pos = float(el_pos[1].text)
	el_pos[0].text = str(x_pos+3.0)
	el_pos[1].text = str(y_pos+0.0)

	#erase_unusedbone(copy_group)
	buat_bone_baru(copy_group)
	if len(varglo.list_new_bone) == 0:
		print(" !!! missing bone controller")
		return

	ganti_guidnya(copy_group)
	masukan_bonebaru(copy_group)
	set_new_shapekey(copy_group)
	varglo.root_file.append(copy_group)
	erase_shapekey()
	
	print('>>>>>>>> cloning shapekey OK <<<<<<<<')

def get_parent(el,level):

	el.set("temp",'sk')
	el_level =''
	for x in range(0,level):
		el_level +='/..'

	el_parent= varglo.root_file.find(".//*[@temp='sk']"+el_level)
	el.attrib.pop('temp')
	
	return el_parent

def create_namesk(el_namebone ,guid):

	el_bone = get_parent(el_namebone,8)
	guid_this = el_bone.get('guid')

	el_origin = el_bone.find(".//origin")
	if not 'guid' in el_origin[0].attrib:
		guid_baru = str(uuid.uuid4())
		el_origin[0].set('guid',guid_baru)

	varglo.el_pos_controller = el_origin[0]

	for sk in varglo.root_file.findall(".//*[@type='skeleton']"):
		for el_sk in sk.findall(".//bone"):
			if el_sk.get('guid')==guid_this:

				el_parent = get_parent(sk,1)
				text_layer = load_template(".//*[@kunci='SK_text_shapekeys']")
				el_string = text_layer.find(".//param/string/..")
				replace(el_string,el_namebone) # karena ada guidnya
				rhs = text_layer.find(".//*[@guid='GUID_controller_pos']/..")
				replace(rhs,varglo.el_pos_controller)
				guid_inf = text_layer.find(".//*[@guid='GUID_toshapekeys']") # konektor
				guid_inf.set('guid',guid)

				text_layer[0].set('active','false') # hide becouse user delete
				el_parent.append(text_layer[0])

def find_controller_nonlist(list_guid_SK):

	list_guid_sk=[]
	list_cont_nodata =[]
	for guid in varglo.smartkey_list:
		list_guid_sk.append(guid[0])

	for cont in list_guid_SK:
		if not cont[0] in list_guid_sk:
			print("  >>> found controller no name,name bone is: ",cont[1])
			varglo.smartkey_list.append([cont[0],cont[1]])

			create_namesk(cont[2],cont[0])

def get_shapekey_list():

	if len(varglo.smartkey_list)>0:
		return

	entry_namesk = varglo.root_file.findall(".//name/join//dynamic_list/entry") # get inf guid code

	if len(entry_namesk) == 0:
		return

	list_guid_SK = []
	for entry in entry_namesk:
		el_namesk = entry.find(".//link_off/string")

		if el_namesk == None: # get controller aktif
			link_off = entry.find(".//link_off")
			el_namesk = link_off.find(".//string")
			#replace(link_off,el_namesk)
			varglo.nama_controller = el_namesk.text
			el_inf = entry.find(".//link_on/realstring/real/")
			varglo.id_controller = el_inf.get('guid')

		name_sk = el_namesk.text
		el_inf = entry.find(".//link_on/realstring/real/")
		list_guid_SK.append([el_inf.get('guid'),name_sk,el_namesk]) 

	list_name_SK = varglo.root_file.findall(".//*[@group='name_SK']")

	if len(list_name_SK) == 0:
		print(" >>> data shapekeys name missing! <<<")

		for guid_this in list_guid_SK:
			varglo.smartkey_list.append([guid_this[0],guid_this[1]])
		
	else:
		idx_name=0
		list_name =[]

		for layer_text in list_name_SK:
			name = layer_text.find(".//param/string")
			name_SK = name.text

			if not name_SK in list_name: # new name if same name
				list_name.append(name_SK)

			else:
				name_SK = name_SK+'_'+str(idx_name)
				name_SK.append(name_SK)

			idx_name +=1
			name.text =name_SK #auto rename

			vcompress = layer_text.find(".//*[@name='vcompress']")
			el_guid = vcompress.find(".//average/entry/")
			guid_this = el_guid.get('guid')

			for guid in list_guid_SK:
				if guid[0]==guid_this:
					text_name = guid[2].text
					varglo.smartkey_list.append([guid_this,text_name])

	find_controller_nonlist(list_guid_SK)

def get_guid_SK(jenis):

	for d in varglo.smartkey_list:
		if jenis == d[1]:
			return d[1],d[0]
	return 'none','none'

def frezzesk(name_shapekey):

	return

	nm_sk,id_sk = get_guid_SK(name_shapekey)
	list_layers = []

	#BLINE REGION
	layer_regions = varglo.root_file.findall(".//*/[@type='region']")
	for layer in layer_regions:
		layer_copy = copy.deepcopy(layer)
		for point_bline in layer_copy.findall(".//bline//point"): # POINT
			if point_bline[0].tag == 'add':
				found_sk = False
				for el_timeloop in  point_bline.findall(".//timeloop"):
					el_id = el_timeloop.find(".//*/[@guid='{no}']".format(no = id_sk))
					if el_id != None:
						if not layer_copy in list_layers:
							list_layers.append(layer_copy)
						wp_temp= None
						for wp in el_timeloop.findall(".//animated/waypoint"):
							
							if wp.get('time')=="-2s":
								pass

							else:
								wp_temp = wp
						if wp_temp !=None:
							found_sk = True
							print("found")
							vec_c = copy.deepcopy(wp_temp[0])
							replace(point_bline,vec_c)

				if not found_sk:
					print("not found")
					el_vec = point_bline.find(".//add/lhs/add//link/vector")
					el_vec_copy = copy.deepcopy(el_vec)
					replace(point_bline,el_vec_copy)

			else:
				pass


def cari_smartkey(awal):

	from GTKtools import show_shapekey_dialog

	jenis = ""

	def ik_load(ikjenis):

		if ikjenis == 'ik1':
			#print("ik2_manual human")
			masukan_templateIK(".//*[@kunci='SK2_template_ik2joint']",".//*[@kunci='SK2_template_ik2joint_layer']")
		if ikjenis == 'ik2':
			#print("ik3_manual animal")
			masukan_templateIK(".//*[@kunci='SK2_template_ik3joint_spider_manual']",".//*[@kunci='SK2_template_ik3joint_spider_manual_layer']")
		if ikjenis == 'ik2b':
			#print("ik3_manual animal spider")
			masukan_templateIK(".//*[@kunci='SK2_template_ik3joint_dino_manual']",".//*[@kunci='SK2_template_ik3joint_dino_manual_layer']")
		if ikjenis == 'ik3':
			#print("ik2_converter human")
			masukan_templateIK(".//*[@kunci='SK2_ikconvereter_2joint']",".//*[@kunci='SK2_ikconvereter_2joint_layer']")
		if ikjenis == 'ik4':
			#print("ik3_converter animal spider")
			masukan_templateIK(".//*[@kunci='SK2_ik3spider']",".//*[@kunci='SK2_ik3spider_layer']")
		if ikjenis == 'ik4b':
			#print("ik3_converter animal")
			masukan_templateIK(".//*[@kunci='SK2_ik3animal']",".//*[@kunci='SK2_ik3animal_layer']")
			
	def pilih_apa(apa):

		if apa == 'new smartkey':
			if jenis == 'ik':
				varglo.ik_smartkey = True

				if wtemplate:
					ik_load(ikjenis)

			elif jenis == 'smartkey':
				varglo.ik_smartkey = False

				if wtemplate:
					masukan_templateSK()

			return apa

		if apa == 'merge':
			merge_skeletons(jenis)
			return apa

		if apa == 'edit':
			varglo.nama_controller,varglo.id_controller = get_guid_SK(jenis)
			return apa

		if apa == 'undo':
			varglo.undo = True
			fileundo_load(jenis)
			return apa

		if apa == 'clone':
			print("   >>> clone doing", jenis)
			if not jenis == None:
				clone_shapekey()
			return apa

		if apa == 'frezze':
			print("   >>> frezze "+jenis+" keys doing")
			print("   >>> undercontruction maybe not work!")
			frezzesk(jenis)

			return apa

	if awal:
		cari_skeleton()
		cari_clone_data()
		get_shapekey_list()
		apa,jenis,wtemplate,ikjenis = show_shapekey_dialog(awal)
		print(apa,jenis,wtemplate,ikjenis)

		if apa == None:
			return None
		else:

			return pilih_apa(apa)
			
	else:
		cari_skeleton()
		cari_clone_data()
		get_shapekey_list()

		if len(varglo.smartkey_list) != 0:
			apa,jenis,wtemplate,ikjenis = show_shapekey_dialog(awal)
			print(apa,jenis,wtemplate,ikjenis)

			if apa == None:
				return None
			else:
				return pilih_apa(apa)

		else:
			return None

def turn_on_keyframes_editmode():

	el_keyframe_this = varglo.root_file.find(".//*[@time='-4s -20f']")
	if el_keyframe_this != None:
		el_keyframe_this.set('active','true')

	else:
		print("   >>> not found keyframe edit mode!")
		metaadd = ET.Element('keyframe')
		metaadd.attrib['time']='-4s -20f'
		metaadd.attrib['active']='true'
		varglo.root_file.insert(1,metaadd)

def add_metamenu(name,isi):
	
	metaadd = ET.Element('meta')
	metaadd.attrib['name']=name
	metaadd.attrib['content']=isi
	varglo.root_file.insert(1,metaadd)

def turnoff_keyframes():

	for meta_keyframes in varglo.root_file.findall(".//keyframe"): 
		meta_keyframes.set('active','false')

def get_totalcontroller(mode):

	total_cont = varglo.root_file.find(".//*[@name='shapekey_count']")
	if total_cont== None:
		varglo.controller = 1
		add_metamenu('shapekey_count',str(varglo.controller))

	else:
		if mode != 'editmode':
			varglo.controller = int(float(total_cont.get('content'))+1)
			total_cont.set('content',str(varglo.controller))

		else:
			name_SK = get_shapekey_aktif()
			name_cont = varglo.nama_controller
			varglo.nama_controller ,varglo.id_controller = get_guid_SK(name_SK)

			if name_cont != varglo.nama_controller:
				print(">>> ! name controller has change")

			set_shapekey_aktif('none',False)
			varglo.controller = int(float(total_cont.get('content'))) # cara lama

	print("   >>> active shapekey ",varglo.nama_controller)

def isi_timelooptemplate(el_temp_valueattime,el_animated):

	el_link_animated = el_temp_valueattime.find(".//*[@nama='SK_link_animated']/..")
	replace(el_link_animated,el_animated)

	el_bone_angle = el_temp_valueattime.find(".//*[@guid='LINK_TO_BONE']/..")

	if varglo.jenis_ik == None:
		replace(el_bone_angle,varglo.el_controller_bone)
		
	else:
		replace(el_bone_angle,varglo.el_angle_IK)
		if varglo.jenis_ik == 'ikmanual':
			replace(el_bone_angle,varglo.el_angle_IK)
		else:
			replace(el_bone_angle,varglo.el_angle_IK)
	el_sud_min = el_temp_valueattime.find(".//*[@value='sud_min']")
	
	el_sud_min.set('value',varglo.sudut_min)
	el_sud_max = el_temp_valueattime.find(".//*[@value='sud_max']")
	el_sud_max.set('value',varglo.sudut_max)

	el_inf = el_temp_valueattime.find(".//*[@guid='LINK_influence']")
	el_inf.set('guid',varglo.influence)

def create_ikmanual_angle(el_link,base_ik):

	el_angle = load_template(".//*[@kunci='SK_BASEangle_IK_manual']")
	el_lhs = el_angle.find(".//valueattime/..")

	el_ik_base_not = el_angle.find(".//*[@value='IK_manual_baseornot']")
	el_ik_tambahan = el_angle.find(".//*[@value='IK_angletambahan']")
	if base_ik:
		el_ik_base_not.set('value','1')
		el_ik_tambahan.set('value',str(varglo.sudutik_to_target))

	else:
		el_ik_tambahan.set('value','0')

	replace(el_lhs,el_link[0])

	el_flip = el_angle.find(".//*[@guid='SK_FLIP']")
	el_flip.set('guid', varglo.guid_flip)

	if varglo.el_angle_IK != None:
		el_vector_t = el_angle.find(".//rhs/vectorangle/vector/subtract/..")
		el_subtract = varglo.el_angle_IK.find(".//vector/subtract")

		if base_ik:
			el_subtract = varglo.el_angle_IK.find(".//vector/subtract")

		else:
			new_this = copy.deepcopy(el_subtract)
			el_temp = new_this[2][0]
			el_temp.set('value','0') # harus dikalikan nol
			el_subtract = new_this

		replace(el_vector_t,el_subtract)

	else:
		print('!!! element SK_angle_IK missing')
	#bagian SK_ORIGIN_TARGET ini isi sesuai data
	return el_angle[0]

def convert_to_timeloop(el_param,base_ik,influence = False):

	if 'inf' in el_param[0].attrib:
		influence = True
		el_param[0].attrib.pop('inf')

	el_temp_valueattime = load_template(".//*[@kunci='SK_shapekey145']")

	for el_type in el_temp_valueattime.findall(".//*[@type='tipe_key']"):
		if el_param[0].get('type') in ['angle','integer','time']:
			el_type.set('type','real')

		else:
			el_type.set('type',el_param[0].get('type'))

	el_link = el_temp_valueattime.find(".//*[@nama='SK_gantisesuaijenis']/..")
	el_rhs = el_temp_valueattime.find(".//*[@nama='SK_base_value']/..")
	el_base = el_param.find(".//*[@time='-2s']/")

	replace(el_rhs,el_base)
	replace(el_link,el_base)

	isi_timelooptemplate(el_temp_valueattime,el_param[0])

	if el_param[0].get('type') in ['angle','integer','time']:
		el_tambahan = None

		if el_param[0].get('type') == 'time':
			el_tambahan = load_template(".//*[@kunci='SK_timetoreal']")
			el_fps = el_tambahan.find(".//*[@value='fps']")
			el_fps.set('value',str(varglo.fps))

		if el_param[0].get('type') == 'angle':
			el_tambahan = load_template(".//*[@kunci='SK2_angle_toreal']")

		if el_param[0].get('type') == 'integer':
			el_tambahan = load_template(".//*[@kunci='SK2_integer_toreal']")

		el_param[0].set('type','real')
		el_link = el_tambahan.find('.//link')

		if varglo.ada_freetime:
			el_link = el_tambahan.find(".//*[@value='SK_valueawal']/..")
			el_link.remove(el_link[0])

		el_link.append(el_temp_valueattime[0])
		el_param.remove(el_param[0])

		if varglo.jenis_ik == 'ikmanual':
			el_angle = create_ikmanual_angle(el_tambahan,base_ik)
			varglo.valueattime_list.append([el_param,el_angle]) # save temporary

		else:
			varglo.valueattime_list.append([el_param,el_tambahan[0]]) # save temporary

	else:
		if influence:
			print("    >>> found influence waypoint")
			guid_this = el_param[0].get('guid')
			el_param[0].attrib.pop('guid')

			el_temp_valueattime[0].set('guid',guid_this)
			el_param.remove(el_param[0])
			varglo.valueattime_list.append([el_param,el_temp_valueattime[0]])

			defs = get_defs()

			for el_sub in defs.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
				if el_sub.tag == 'link':
					replace(el_sub,el_temp_valueattime[0])

			for val in varglo.valueattime_list: # replace in timeloop data
				for el_link in val[1].findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
					replace(el_link,el_temp_valueattime[0])

		else:
			el_param.remove(el_param[0])
			varglo.valueattime_list.append([el_param,el_temp_valueattime[0]]) # save temporary

def ganti_animated_zero(el_animated):

	vec_x = 0
	vec_y = 0
	real_v = 0

	for wp in el_animated.findall(".//waypoint"):
		timet = wp.get('time')

		if timet == '-7.2s':
			if 'guid' in wp[0].attrib:
				wp[0].attrib.pop('guid')

			if el_animated.get('type')== 'vector':
				vec_x = float(wp[0][0].text)
				vec_y = float(wp[0][1].text)
				wp[0][0].text = '0.0' # isi menjadi nol
				wp[0][1].text = '0.0'

			if el_animated.get('type') in ['real','angle','integer']:
				real_v =  float(wp[0].get('value'))
				wp[0].set('value','0.0')

		else:
			if timet != '-2s':

				if 'guid' in wp[0].attrib:
					wp[0].attrib.pop('guid')

				if el_animated.get('type')== 'vector':
					if 'guid' in wp[0].attrib:
						wp[0].attrib.pop('guid')

					vec_x_new = float(wp[0][0].text)
					vec_y_new = float(wp[0][1].text)

					vec_x_new -= vec_x
					vec_y_new -= vec_y

					wp[0][0].text = str(vec_x_new)
					wp[0][1].text = str(vec_y_new)

				if el_animated.get('type') in ['real','angle','integer']:
					real_v_new =  float(wp[0].get('value'))
					real_v_new -= real_v
					wp[0].set('value',str(real_v_new))

def convert_to_real(el_animated):

	for el_angle in el_animated.findall('.//angle'):
		el_angle.tag = 'real'

	for el_angle in el_animated.findall('.//integer'):
		el_angle.tag = 'real'

def ganti_timez(el_layer_f,selisih_time, influence = False):

	#animated = False

	for el_ani_f in el_layer_f.findall(".//waypoint/.."):# cari animasi perbagian, misal point, radius, (bagian di bline) dan param di layer umum
		if  el_ani_f.get('type') in ['vector','real','angle','integer','time']:
			base_wp = None
			begin_wp = None
			end_wp = None
			ada_base_wp = False
			key_total = 0
			last_key = False

			for wp in el_ani_f.findall(".//waypoint"):
				timet = wp.get('time')
				timef = float(timet.strip("s"))
				timer = round(timef, 3)

				if  timer >= (varglo.time_left) and timer <= (varglo.time_right): #wilayah input frame
					if timer == varglo.time_left: # ambil base value
						base_wp = copy.deepcopy(wp)

					if timer == varglo.time_right:
						last_key = True
						
					new_timer = round(selisih_time+timer,6)
					wp.set('time',str(new_timer)+'s')

					if key_total == 0: #create begin wp
						begin_wp = copy.deepcopy(wp)
						begin_wp.set('time',str(varglo.time_left)+'s')

					end_wp = copy.deepcopy(wp)
					key_total +=1

				if timet == '-2s':
					ada_base_wp = True
					el_ani_f.remove(wp)

			if base_wp != None: # masukan base value di -50f/-2s
				if key_total == 1: # if user fill only first key / only one key
					print("       >>> found only 1 waypoint on [ "+(el_layer_f.tag)+" ] auto create new waypoint at last time")
					
					end_wp = copy.deepcopy(base_wp)
					new_timer = round(selisih_time+varglo.time_right,6)
					end_wp.set('time',str(new_timer)+'s')
					el_ani_f.append(end_wp)
					
				if key_total >1: # jika last key not in time_right /-2.8

					if not last_key:
						print("       >>> missing waypoint End time on [ "+(el_layer_f.tag)+" ] auto create new waypoint at End time")
						new_timer = round(selisih_time+varglo.time_right,6)
						end_wp.set('time',str(new_timer)+'s')
						el_ani_f.append(end_wp) # append close wp. with last wp
				
				if 'guid' in base_wp.attrib:
					base_wp.attrib.pop('guid')

				base_wp.set('time',str(varglo.time_base)+'s')
				el_ani_f.append(base_wp)
				animated = True

			else:
				#animated = False
				print("       >>> waypoint start missing on [ "+(el_layer_f.tag)+" ] auto create new waypoint at start time")

				if key_total == 1: 
					print("       >>> found only 1 waypoint on [ "+(el_layer_f.tag)+" ]")

				if begin_wp != None:
					guid_el = begin_wp[0]
					if 'guid' in guid_el.attrib:
						guid_el.attrib.pop('guid')

					new_timer = round(selisih_time+varglo.time_left,6)
					begin_wp.set('time',str(new_timer)+'s')
					el_ani_f.insert(0,begin_wp)
					
					if not last_key:
						new_timer = round(selisih_time+varglo.time_right,6)
						end_wp.set('time',str(new_timer)+'s')
						el_ani_f.append(end_wp) # append close wp. with last wp

					base_wp = copy.deepcopy(begin_wp)
					base_wp.set('time',str(varglo.time_base)+'s')
					el_ani_f.append(base_wp) #create base wp

				if ada_base_wp:
					print("<--- not found key at -120f as base shape make sure your key is right!! ")

			if  el_ani_f.get('type') in ['angle','integer','time']:
				convert_to_real(el_ani_f)

			if el_ani_f.get('type') == 'time':
				convert_time_toreal(el_ani_f)

			ganti_animated_zero(el_ani_f)
	#return animated

def set_split_bline_point(el_param_f):

	if el_param_f.tag in ['split','split_radius','split_angle']:
		el_this = el_param_f.find(".//bool")

		if el_param_f.tag == 'split_angle': #set default split_angle is false
			el_this.set('value','false')

		if el_param_f.tag == 'split_radius': #set default split_angle is false
			el_this.set('value','true')

		replace(el_param_f,el_this) #del all animaetd value for this element

def cek_sudah(el_animated):

	el_base = el_animated.find(".//*[@time='-2s']")

	if el_base != None:
		return True

	else:
		return False

def convert_time_toreal(el_this):

	for wp in el_this.findall('.//waypoint'):
		wp[0].tag = 'real'
		time = wp[0].get('value')
		timef = float(time.strip("s"))
		timef = round(timef, 5)
		timef = timef*varglo.fps
		wp[0].set('value',str(timef))

def cek_wp_negatif(el_animated):

	negatifwp = True

	for wp in el_animated.findall('.//waypoint'):
		timet = wp.get('time')
		timef = float(timet.strip("s"))
		timer = round(timef, 3)

		if timer >=0:
			negatifwp = False
			break

	return negatifwp

def convert_to_realcolor(el_this):

	data = {'r':'red','g':'green','b':'blue','a':'alpha'}

	el_color = load_template(".//*[@kunci='SK_COLORTOREAL']")

	for kode in data:
		animated = copy.deepcopy(el_this[0])

		el_wp = []

		for wp in animated.findall('.//waypoint'):
			color_c = copy.deepcopy(wp[0])
			el_real = load_template(".//*[@kunci='SK_REAL']")
			el_kode = color_c.find('.//'+kode)
			value_nya = el_kode.text
			el_real[0].set('value',value_nya)
			replace(wp,el_real[0])		
			el_wp.append(wp)	
		
		warna = data[kode]
		el_warna_this = el_color.find('.//'+warna)

		for el_wp in el_wp:
			el_warna_this[0].append(el_wp)

	replace(el_this,el_color[0])

def convert_shapekeylama(el_link):

	el_link_parent = get_parent(el_link,6)

	el_add = el_link_parent[0]

	selisih_time = get_selisih_time()

	value_this = get_shapekey_aktif()
	if value_this == 'None': # mode inputkey bukan edit

		# new shapekey in layer shapekeyed
		el_link = el_add.find('.//link')

		if el_link[0].tag == 'animated':
			type_ani = el_link[0].get('type')
			ganti_timez(el_link,selisih_time)

			el_ani_timeloop = copy.deepcopy(el_link[0])
			if 'guid' in el_ani_timeloop.attrib:
				guid_this = el_ani_timeloop.get('guid')
				el_ani_timeloop.attrib.pop('guid')

			update_all_base_new(el_add,el_ani_timeloop)

			el_skala = el_add.find('.//scalar/')
			el_skala.set('value','0')

			el_skala2 = el_tobe_export.find('.//rhs/scale/scalar/')

			val_average = 1
			el_skala2.set('value',str(val_average))

def cek_waypoint_atcont(el_animateds): # check is waypoint in controller angle, if yes remove all animated at contoller angle

	def set_to_nonanimated(el_animated,el_this,tipe):

		def print_tipe(tipe):

			if tipe == 'angle':
					print("       >>> found animated in angle controller not processing!!")

			if tipe == 'scalelx':
				print("       >>> found animated in length bone controller not processing!!")

			if tipe == 'origin':
				print("       >>> found animated in target IK bone controller not processing!!")


		el_layer = get_parent(el_this,1)

		if el_layer.tag == 'bone':
			el_name = el_layer.find(".//name/join")

			if el_name != None:
				print_tipe(tipe)
				
				if tipe in ['angle','scalelx']:
					guid_this = el_animated[0].get('guid')
					el_real = el_this.find(".//real")
					el_real.set('guid', guid_this)
					copy_el_real = copy.deepcopy(el_real)
					replace(el_animated,copy_el_real)

					for el_link in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)): # replace all 
						if el_link.tag == 'link':
							replace(el_link,copy_el_real)

					for val in varglo.valueattime_list: # replace in timeloop data
						for el_lhs in val[1].findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
							replace(el_lhs,copy_el_real)

				if tipe == 'origin':
					guid_this = el_this[0].get('guid')

					el_vector= el_this.find(".//vector")
					copy_el_vector = copy.deepcopy(el_vector)
					replace(el_animated,copy_el_vector)

					for el_link in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)): # replace all 
						if el_link.tag in ['link_target','rhs']:
							replace(el_link,el_this[0])

					for val in varglo.valueattime_list: # replace in timeloop data
						for el_lhs in val[1].findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
							replace(el_lhs,el_this[0])

	for el_this in el_animateds: 
		if el_this.tag == "link":# angle
			up_el = get_parent(el_this,2)

			if up_el.tag == 'angle': # angle of controller??
				set_to_nonanimated(el_this,up_el,'angle')
						
		if el_this.tag == "scalelx":
			set_to_nonanimated(el_this,el_this,el_this.tag)

		if el_this.tag == "lhs":
			up_el = get_parent(el_this,2)

			if up_el != None:
				if up_el.tag == 'origin': # origin of controller??
					set_to_nonanimated(el_this,up_el,'origin')

def set_guid_listinf():

	bones = varglo.root_file.find(".//bones")

	guid_this = None
	for bone in bones.findall(".//bone"):
		for ani_inf in bone.findall(".//scalex//entry/animated"):
			guid_this = ani_inf.get('guid')

			if not guid_this in varglo.list_guid_inf:
				varglo.list_guid_inf.append(guid_this)

def cari_in_layer(): # di param umum

	print(' ')
	print("   [.] searching comon layers")

	set_guid_listinf()

	selisih_time = get_selisih_time()
	el_defs = get_defs()

	el_animateds = varglo.root_file.findall(".//animated/..")
	cek_waypoint_atcont(el_animateds)

	for el_param_f in el_animateds:

		if el_param_f.tag == 'defs':
			print("   >>> animated in exported not processing!!")
			continue

		if not cek_wp_negatif(el_param_f): #jika animasi tidak negatif time maka itu diluar data input maupun edit
			continue

		if cek_sudah(el_param_f): # cek sudah di dalam time line data
			continue

		base_ik = False

		if el_param_f.tag == 'angle':
			el_param_f_parent = get_parent(el_param_f,1)

			if 'base' in el_param_f_parent.attrib:
				base_ik = True
				el_param_f_parent.attrib.pop('base')

		set_split_bline_point(el_param_f)

		if el_param_f.tag in ['width','origin']:

			if el_param_f[0].get('type')== 'real':
				el_this = el_param_f.find(".//real")
				el_realss = el_param_f.findall(".//real")
				val_base = el_this.get('value')
				val_same =False
				
				if len(el_realss)>=2:
					for val in el_realss:
						val_this = val.get('value')
						if val_base == val_this:
							val_same = True

				if val_same:
					replace(el_param_f,el_this)
		
		if el_param_f[0].get('type') in ['vector','real','integer','angle','time','color']:
			if 'guid' in el_param_f[0].attrib:
				if el_param_f[0].get('guid') in varglo.list_guid_inf:
					el_param_f[0].set("inf","animated")

			if  el_param_f[0].get('type')== 'color':
				convert_to_realcolor(el_param_f)

				for el_co in el_param_f.findall(".//animated/.."):

					ganti_timez(el_co,selisih_time)
					convert_to_timeloop(el_co,base_ik)
				continue

			if  el_param_f[0].get('type')== 'time':
				el_layer_parent = get_parent(el_param_f,1)

				if el_layer_parent.tag == 'layer':
					if 'type' in el_layer_parent.attrib:
						if el_layer_parent.get('type') == 'freetime': #if FREETIME LAYER
							varglo.ada_freetime = True
							print('>>> found freetime layer convert to shapekey canceled for some layers')

			ganti_timez(el_param_f,selisih_time)
			convert_to_timeloop(el_param_f,base_ik)

	print("   [..]")
	print(" ")

def move_timeto_data(el_ani,selisih_time):

	ganti_timez(el_ani,selisih_time)

def cek_sudah_update(el_animated):

	wp_pertama = el_animated.find('.//waypoint')
	timet = wp_pertama.get('time')
	timef = float(timet.strip("s"))
	timef = round(timef, 5)

	if timef == -7.2: 
		return True

	else:
		return False

def update_all_base_new(el_add,el_ani): #basedata

	el_base = el_ani.find(".//*[@time='-2s']")

	if el_base != None:
		# GANTI BASE EL 
		el_rhs = el_add.find('.//lhs/add/rhs')
		replace(el_rhs,el_base[0])

		el_link = el_add.find('.//lhs//link')
		replace(el_link,el_base[0])
		#GANTI ANIMASI BASE YANG LAIN

		for el_entry in el_add.findall('.//entry/timeloop/..'):
			#harusnya mesti tidak terait dengan edit tetap jika element tersebut sudah ada shapekey akan di perbaruihi juga basenya.DONE
		
			#el_entry.attrib.pop('shapekey')
			el_animated = el_entry.find('.//link/animated')
			#if cek_sudah_update(el_animated):
				#continue
			el_2s = el_animated.find(".//*[@time='-2s']") 
			el_wp_base = copy.deepcopy(el_2s)
			#varglo.controller_data.append([el_wp_base,el_base[0],"replace"])
			replace(el_2s,el_base[0]) # update bagian -2s

			type_ani = el_animated.get('type')
			vec_x = 0
			vec_y = 0
			real_v = 0

			for wp in el_animated.findall(".//waypoint"):
				timet = wp.get('time')
				timef = float(timet.strip("s"))
				timef = round(timef, 5)
			
				if not timef in [-7.2,-2.0]:
					if type_ani == "vector":
						vec_x = float(el_base[0][0].text)
						vec_y = float(el_base[0][1].text)

						vec_x_awal = float(el_wp_base[0][0].text)
						vec_y_awal = float(el_wp_base[0][1].text)

						vec_x_current = float(wp[0][0].text)
						vec_y_current = float(wp[0][1].text)

						vec_temp_x = (vec_x_current+vec_x_awal)-vec_x
						vec_temp_y = (vec_y_current+vec_y_awal)-vec_y

						wp[0][0].text = str(vec_temp_x)
						wp[0][1].text = str(vec_temp_y)

					if type_ani in ['real','angle','integer']:
						real_value = float(el_wp_base[0].get('value'))
						real_value_awal = float(wp[0].get('value'))
						real_value_baru = float(el_base[0].get('value'))

						real_temp_v = (real_value_awal+real_value)-real_value_baru
						wp[0].set('value',str(real_temp_v))

	else:
		print('missing base value')

def update_all_base(el_add,el_ani): #basedata

	el_base = el_ani.find(".//*[@time='-2s']")

	if el_base != None:
		el_rhs = el_add.find('.//lhs/add/rhs')
		replace(el_rhs,el_base[0])

		el_link = el_add.find('.//lhs//link')
		replace(el_link,el_base[0])
		#GANTI ANIMASI BASE YANG LAIN

		for el_entry in el_add.findall('.//entry/timeloop/..'):
			el_animated = el_entry.find('.//link/animated')
			el_2s = el_animated.find(".//*[@time='-2s']") 
			el_wp_base = copy.deepcopy(el_2s)
			replace(el_2s,el_base[0]) # update bagian -2s

			type_ani = el_animated.get('type')
			vec_x = 0
			vec_y = 0
			real_v = 0

			for wp in el_animated.findall(".//waypoint"):
				timet = wp.get('time')
				timef = float(timet.strip("s"))
				timef = round(timef, 5)
			
				if not timef in [-7.2,-2.0]:
					if type_ani == "vector":
						vec_x = float(el_base[0][0].text)
						vec_y = float(el_base[0][1].text)

						vec_x_awal = float(el_wp_base[0][0].text)
						vec_y_awal = float(el_wp_base[0][1].text)

						vec_x_current = float(wp[0][0].text)
						vec_y_current = float(wp[0][1].text)

						vec_temp_x = (vec_x_current+vec_x_awal)-vec_x
						vec_temp_y = (vec_y_current+vec_y_awal)-vec_y

						wp[0][0].text = str(vec_temp_x)
						wp[0][1].text = str(vec_temp_y)

					if type_ani in ['real','angle','integer']:
						real_value = float(el_wp_base[0].get('value'))
						real_value_awal = float(wp[0].get('value'))
						real_value_baru = float(el_base[0].get('value'))

						real_temp_v = (real_value_awal+real_value)-real_value_baru
						wp[0].set('value',str(real_temp_v))

	else:
		print('missing base value')

def find_influence_key(el_add):

	el_inf = el_add.find(".//*/[@info='influence']")

	if el_inf != None:
		print('    found element influence animated')
		el_inf.attrib.pop('info')
		varglo.valueattime_list.append([el_inf,varglo.el_influence])

	else:
		pass

	#print('    [..] Done')

def cari_thisname(this_name,el_add_copy,el_defs):

	for el_add in el_defs.findall(".//*[@id]"):
		if el_add.get('id') != this_name:
			for this_el in el_add.findall(".//*/[@link='{no}']".format(no=this_name)):
				this_el.attrib.pop('link')
				el_temp = el_add_copy.find('.//link')
				el_link_p = copy.deepcopy(el_temp)
				replace(el_link_p,el_add_copy)
				this_el.append(el_link_p)

def erase_shapekey():

	for el_ani in varglo.root_file.findall('.//animated'):
		wps = el_ani.findall('.//waypoint')
		if len(wps) == 0:
			el_ani.set('temp','shapekey')
			el_ani_parent = varglo.root_file.find(".//*[@temp='shapekey']/../../../../../..")

			if el_ani_parent.tag == 'scale':
				el_skalar = el_ani_parent.find('./scalar/')
				value_this = int(float(el_skalar.get('value')))

				if value_this == 1:
					el_ani.attrib.pop('temp')
					el_ani_parent.set('temp','shapekey')
					el_base = varglo.root_file.find(".//*[@temp='shapekey']/../../..")
					el_ani_parent.attrib.pop('temp')
					el_base_rhs = el_base.find('.//add/lhs/add/rhs')
					el_base_value = copy.deepcopy(el_base_rhs[0])

					if 'guid' in el_base_value.attrib:
						el_base_value.attrib.pop('guid')

					replace(el_base,el_base_value)

				else:
					value_this -= 1
					el_skalar.set('value',str(value_this)) # isi dengan yaang baru

					#del entry
					el_ani_entry = varglo.root_file.find(".//*[@temp='shapekey']/../../..")
					el_average = el_ani_parent[0][0]
					el_average.remove(el_ani_entry)

					el_ani.attrib.pop('temp')


def find_inf_controlled(el_add):

	el_inf = el_add.find(".//map_range/link")
	if not el_inf == None:
		print(el_inf[0].tag)

def find_di_defs(type):

	print(' ')
	print("   [.] searching timeloop in defs")

	el_defs = varglo.root_file.find(".//defs")
	selisih_time = get_selisih_time()

	if el_defs != None:
		for el_add in el_defs.findall(".//*[@id]"):
			ada_shapekey = False
			varglo.found_keys += 1

			#find_inf_controlled(el_add)
			#find_waypoint_incont(el_add)

			if 'inf_' in el_add.get('id'):
				el_defs.remove(el_add)
				continue

			if 'guid' in el_add.attrib:
				print('    ada guidnya at |',el_add.get('id'))
			
			for el_entry in el_add.findall(".//average/entry"):
				
				if 'shapekey' in el_entry.attrib: # jika mode edit dan masuk ke dalam edit aktif
					ada_shapekey = True
					#el_entry.attrib.pop('shapekey')#hapus kode
					el_link = el_entry.find('.//timeloop/link')

					if (len(el_link))== 0: #karena bline ada region dan out line
						el_defs.remove(el_add) #
						continue

					el_add_parent = get_parent(el_link,1)

					if 'guid' in el_add_parent.attrib:
						el_add_parent.attrib.pop('guid')

					#if 'shapekey_21' == el_add.get('id'): # apa fungsinya???
						#el_link.set('temp','shapekey') 
						#el_add_parent = varglo.root_file.find(".//*[@temp='shapekey']/..")
						#el_link.attrib.pop('temp')

					move_timeto_data(el_link[0],selisih_time)
					update_all_base(el_add,el_link[0])

					guid_this = el_link[0].get('guid')
					el_add_copy = copy.deepcopy(el_add)

					el_add_copy.attrib.pop('id')
					el_defs.remove(el_add) #
					# ganti semua timeloop dan del sementara
					for el_awal in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
						el_awal.remove(el_awal[0])
						varglo.valueattime_list.append([el_awal,el_add_copy])

			if not ada_shapekey:
				el_rhs = el_add.find('.//lhs/add/rhs')

				if el_rhs != None:
					if el_rhs[0].tag == 'animated':
						type_ani = el_rhs[0].get('type')
						ganti_timez(el_rhs,selisih_time)

						el_ani_timeloop = copy.deepcopy(el_rhs[0])

						if 'guid' in el_ani_timeloop.attrib:
							guid_this = el_ani_timeloop.get('guid')
							el_ani_timeloop.attrib.pop('guid')

						update_all_base(el_add,el_ani_timeloop)

						el_temp_timeloop = load_template(".//*[@kunci='SK_shapekey145']")
						for el_type in el_temp_timeloop.findall(".//*[@type='tipe_key']"):

							if type_ani in  ['angle','integer']:
								el_type.set('type','real')

							else:
								el_type.set('type',type_ani)

						isi_timelooptemplate(el_temp_timeloop,el_ani_timeloop)

						el_scale = el_add.find('.//link/average/../..')
						el_average = el_scale.find('.//link/average')

						el_timeloop_entry_baru = el_temp_timeloop.find('.//average/entry')
						el_average.append(el_timeloop_entry_baru)
						#el_scalar = el_scale.find('.//scalar/real') # upate average pembagi
						el_total = el_scale.findall('.//average/entry')
						el_scale[1][0].set('value',str(len(el_total)))

						el_add_copy = copy.deepcopy(el_add)
						el_add_copy.attrib.pop('id')
						el_defs.remove(el_add)

						for el_awal in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
							el_awal.remove(el_awal[0])
							varglo.valueattime_list.append([el_awal,el_add_copy])

					else:
						if 'guid' in el_rhs[0].attrib:
							guid_this = el_rhs[0].get('guid')
							el_rhs[0].attrib.pop('guid')

							el_add_copy = copy.deepcopy(el_add)
							el_defs.remove(el_add)

							if 'guid' in el_add_copy.attrib:
								el_add_copy.attrib.pop('guid')
								name_shapekey = el_add_copy.get('id')
								this_name = el_add_copy.get('id')
								el_add_copy.attrib.pop('id')
								cari_thisname(this_name,el_add_copy,el_defs) # cari apakah di defs lain ada pengunaan influence dari data ini
								varglo.el_influence = el_add_copy

							else:
								el_add_copy.attrib.pop('id')

								for el_map in el_add_copy.findall('.//map_range'):
									if 'link' in el_map.attrib: # terkoneksi dengan influence
										el_map.attrib.pop('link')

										if varglo.el_influence != None:
											el_link = varglo.el_influence.find('.//link')
											el_link_temp = copy.deepcopy(el_link)
											varglo.el_influence.set('guid',guid_this)
											replace(el_link_temp,varglo.el_influence)
											el_map.append(el_link_temp) # ADD LINK KE INFLUENCE DATA

							find_influence_key(el_add_copy)

							for el_awal in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
								el_awal.remove(el_awal[0])
								varglo.valueattime_list.append([el_awal,el_add_copy])

						else:
							el_defs.remove(el_add)
							print("del export no related")


	else:
		print('   !!! not found in defs')

	print("   [..]")

def convert_keys_tolinear(file):

	for wp in file.findall(".//waypoint"):
		time = wp.get('time')
		timef = float(time.strip("s"))

		if timef < 0:# ONLY time NEGATIF
			if wp.get('before') !='linear':
				wp.set('before','linear')

			if wp.get('after') !='linear':
				wp.set('after','linear')

def cari_defs_this(guid_this):

	defs = get_defs()

	for el_add in defs.findall(".//*[@id]"):
					
		if 'inf_' in el_add.get('id'):
			for el_inf in el_add.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
				return el_add

	return None

def cari_link_inf(el_this,defs):

	guid_this = el_this[0].get('guid')

	for el_add in defs.findall(".//*[@id]"):
		if 'inf_' in el_add.get('id'):
			el_inf = copy.deepcopy(el_add)
			el_inf.attrib.pop('id')
			el_rhs = el_inf.find('.//lhs/add/rhs/')
			guid_lama = el_rhs.get('guid')
			el_rhs.attrib.pop('guid')
			el_inf.set('guid',guid_lama)

			defs.remove(el_add)

			if guid_this == guid_lama:
				for el_link in defs.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
					if el_link.tag == 'link':
						replace(el_link,el_inf)

			replace(el_this,el_inf)

def find_keyed_influence():

	defs = get_defs()

	print('   [.] get influence')
	selisih_time = get_selisih_time()

	el_bones = varglo.root_file.find(".//bones")

	for el_this in el_bones.findall('.//scalex/switch//link_on/average/entry'):
		if el_this[0].tag == 'animated':
			#print('    found animated influence |',el_this[0].attrib)
			el_wp_base = el_this[0].find(".//*[@time='-2s']") 
			
			if el_wp_base == None:
				ganti_timez(el_this[0],selisih_time)
				convert_to_timeloop(el_this,False,True)
			else:
				guid_this = el_this[0].get('guid')
				ganti_timez(el_this[0],selisih_time)
				el_this[0].attrib.pop('guid')
				el_new_animated= copy.deepcopy(el_this[0])
				defs = get_defs()

				el_influence = None
				el_defs_ada_this = cari_defs_this(guid_this)# cari defs sesuai guid this

				if el_defs_ada_this != None:
					el_defs_ada_this.attrib.pop('id')
					el_defs_ada_this.set('guid',guid_this)
					el_influence  = copy.deepcopy(el_defs_ada_this)
					varglo.el_influence = el_influence

					for el_inf in el_influence.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
						replace(el_inf,el_new_animated)

					defs.remove(el_defs_ada_this)
					replace(el_this,el_influence)

		else:
			#masih ada yg error. tidak bisa balik data influence  
			cari_link_inf(el_this,defs)

	print('   [..] done')

def find_animasi_dan_convert(type):

	if len(varglo.data_error) >0:
		return

	hide_animated_controllerik() # hide el animated key in bone ik

	print(" ")
	print("[.] searching animated and converted to timeloop")

	if varglo.ik_smartkey:
		pass
	else:
		if type == 'editmode':
			pass
	split_bline()
	find_di_defs(type) # cari di defs dan hilangkan sementara 
	cari_in_layer()

	print("[..] OK Done:")

def set_nama_jadireverse(bone):

	el_name = bone.find(".//name")
	name = copy.deepcopy(el_name[0])
	el_grey = load_template(".//*[@kunci='SK_greykode']")
	el_grey[0].tag = 'reverse'
	el_link = el_grey.find(".//link")
	replace(el_link,name)
	el_name_copy = copy.deepcopy(el_grey[0])
	varglo.controller_data.append([el_name,el_name_copy,"replace"])

def set_shapekey_aktif(name_SK,aktifkan):

	meta_shapekey = varglo.root_file.find(".//*[@name='shapekey_aktif']")

	if meta_shapekey == None:
		if aktifkan:
			add_metamenu('shapekey_aktif',varglo.nama_controller)
		else:
			add_metamenu('shapekey_aktif',name_SK)

	else:
		if aktifkan:
			meta_shapekey.set('content',varglo.nama_controller)
			
		else:
			meta_shapekey.set('content',name_SK)

def get_shapekey_aktif():

	meta_shapekey = varglo.root_file.find(".//*[@name='shapekey_aktif']")

	if meta_shapekey == None:
		return 'none'
	else:
		return meta_shapekey.get('content')

def set_kode_toreferen(el_bone):

	print('   >>> reference')

	el_string = None

	if varglo.id_controller  == 'none':
		print(">>> ! id shapekey missing")
		el_string = el_bone.find(".//name//link_off")

	else:
		el_name_this = el_bone.find(".//name")
		#print(el_name_this)
		el_entry = el_name_this.find(".//*/[@guid='{no}']/../../../../..".format(no = varglo.id_controller))
		if el_entry != None:
			el_string = el_entry.find(".//link_off")
			#print(el_entry.tag)

	el_string_copy = copy.deepcopy(el_string[0])
	el_temp = load_template(".//*[@kunci='SK_REFERENCE']/")
	el_link = el_temp.find(".//link")

	replace(el_link,el_string_copy)
	replace(el_string,el_temp)

def get_bonebaseik(el_bones,guid_controller):

	for el_sub in el_bones.findall(".//*/[@guid='{no}']/../..".format(no = guid_controller)):
		
		if el_sub.tag in ['subtract','ik']:
			guid_this = None

			if el_sub.tag =='subtract':
				el_base = el_sub.find('.//rhs/add')
				
				if el_base != None:

					guid_this = el_base.get('guid')

			else:

				el_base = el_sub.find('.//link_pole/add')
				guid_this = el_base.get('guid')

			for el_bone_baseik in el_bones.findall(".//*/[@guid='{no}']/../..".format(no = guid_this)):
				if el_bone_baseik.tag == 'bone':
					return el_bone_baseik

def set_origin_base(el_bone_baseik):

	el_origin = el_bone_baseik.find('.//origin')
	guid_this = el_origin[0].get('guid')
	el_origin[0].attrib.pop('guid')
	origin_this = copy.deepcopy(el_origin[0])

	el_origin_edit = el_bone_baseik.find('.//bone_depth//vectorlength/vector')
	el_origin_edit[0].set('guid',guid_this)
	el_origin_edit_new = copy.deepcopy(el_origin_edit[0])

	varglo.controller_data.append([el_origin,el_origin_edit_new,'replace'])
	replace(el_origin_edit,origin_this)

	for el_this in  varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
		replace(el_this,el_origin_edit_new)

def get_origin_target(el_bones,guid_controller):

	for bone_target_origin in el_bones.findall(".//*/[@guid='{no}']/..".format(no = guid_controller)):
		if bone_target_origin.tag == 'origin':
			return bone_target_origin

	return None

def get_angle_controller(guid_controller,el_bones):

	el_angle = el_bones.find(".//*/[@guid='{no}']/..".format(no = guid_controller))

	if el_angle != None:
		for el_bone in el_bones.findall(".//*/[@guid='{no}']/../../../..".format(no = guid_controller)):
			if el_bone.tag == "bone":
				return el_angle
	else:
		print(" not found controller!!")
		return None

def move_animasi_thiske_editmode(el_animated, edit):

	varglo.user_animated_target = copy.deepcopy(el_animated)

	user_animated = False
	for wp in el_animated.findall('.//waypoint'):
		time = wp.get('time')
		time_temp = float(time.strip("s"))

		if time_temp >= 0.0:
			user_animated = True
			el_animated.remove(wp)
			continue

		add_time =- 2.4
		if edit:
			add_time = 2.4

		timef = time_temp+add_time
		timef = round(timef, 3)
		wp.set('time',str(timef)+'s')

	if user_animated:
		for wp in varglo.user_animated_target.findall('.//waypoint'):
			time = wp.get('time')
			time_temp = float(time.strip("s"))

			if time_temp >= 0.0:
				continue

			else:
				varglo.user_animated_target.remove(wp)

	else:
		varglo.user_animated_target = None

def get_type_cont(guid):

	bones = varglo.root_file.find(".//bones")
	for el_this in bones.findall(".//*/[@guid='{no}']/..".format(no = guid)):
		if el_this.tag == 'scalelx':
			varglo.type_controller = 'length'
			el_parent = get_parent(el_this,1)
			set_kode_toreferen(el_parent)
			return el_this,'length'

		if el_this.tag == 'link':
			el_parent = get_parent(el_this,1)
			if el_parent.tag == 'fromreal':
				el_parent = get_parent(el_this,3)
				set_kode_toreferen(el_parent)
				return el_this,'angle'

def set_controllertomode_editz(el_add,guid_controller,value_sud): # jadikan bone angle jenis animasi

	el_bones = varglo.root_file.find(".//bones")
	el_controller = None

	if varglo.jenis_ik == None:

		el_link_controller,jenis = get_type_cont(guid_controller)

		if not jenis == 'length':
			el_link_controller = get_angle_controller(guid_controller,el_bones)
		#ganti_namabone(el_bone) # ganti cara 
		# DATA AWAL DISIMPAN SEHINGGA JIKA BALIK KE MODE AWAL BISA KEMBALI KE SUDUT AWAL
		el_link = load_template(".//*[@kunci='SK_animated_controller']") # load switch template 

		el_switch = el_link.find(".//switch")
		el_switch.set('guid',guid_controller)

		el_sud_min = el_link.find(".//*[@value='sud_min']")
		el_sud_min.set('value',varglo.sudut_min)
		el_sud_max = el_link.find(".//*[@value='sud_max']")
		el_sud_max.set('value',varglo.sudut_max)
		#el_sud_awal = el_link.find(".//*[@value='value_sud_awal']")
		el_sud_awal = el_link.find(".//*[@value='value_sud_awal']/..")

		if value_sud.tag == "animated":
			replace(el_sud_awal,value_sud)
			
		else:
			replace(el_sud_awal,value_sud)

		el_controller = el_link[0]
		replace(el_link_controller,el_link[0])

	else:
		origin_target = get_origin_target(el_bones,guid_controller)
		bone = get_parent(origin_target,1)
		set_kode_toreferen(bone)

		el_bone_baseik = get_bonebaseik(el_bones,guid_controller)

		set_nama_jadireverse(el_bone_baseik)
		set_origin_base(el_bone_baseik)

		#origin_target = bone.find('.//origin')
		guid_this = origin_target[0].get('guid')
		origin_target[0].attrib.pop('guid')
		origin_target_awal = copy.deepcopy(origin_target[0])

		ani_temp = bone.find('.//bone_depth//vectorlength/')
		if ani_temp == None:
			print("!!! broken file data controller !!!")
			#becarefull dont try to delete this code in file synfig

		el_target_animasi_original = copy.deepcopy(ani_temp[0])
		el_target_animasi_original.set('guid',guid_this)

		move_animasi_thiske_editmode(el_target_animasi_original,True)
		
		el_controller = el_target_animasi_original
		replace(ani_temp,origin_target_awal)

		varglo.controller_data.append([origin_target,el_target_animasi_original,'replace'])
	# GANTI SEMUA TERKAIT CONTROLLER
	for el_sud in  varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_controller)):
		replace(el_sud,el_controller)

def ganti_animasi_keawal(el_animated): # pindahkan ke area edit

	type_ani = el_animated.get('type')
	el_wp_base = el_animated.find(".//*[@time='-2s']") # beri kode greyed
	el_base = copy.deepcopy(el_wp_base[0])

	if 'guid' in el_base.attrib:
		el_base.attrib.pop('guid')

	if type_ani == "vector":
		vec_x_awal = float(el_wp_base[0][0].text)
		vec_y_awal = float(el_wp_base[0][1].text)

		idx =0 
		for wp in el_animated.findall('.//waypoint'):
			if idx == 0:
				wp.set('time','-4.8s')
				replace(wp,el_base)

			else:
				if wp.get('time') != "-2s":
					time = wp.get('time')
					timef = float(time.strip("s"))+2.4
					timef = round(timef, 3)
					wp.set('time',str(timef)+'s')
					vec_x_new = float(wp[0][0].text)+vec_x_awal
					vec_y_new = float(wp[0][1].text)+vec_y_awal
					wp[0][0].text = str(vec_x_new)
					wp[0][1].text = str(vec_y_new)

			idx +=1

	if type_ani == "real":
		val_r_awal = float(el_base.get('value'))

		idx =0 
		for wp in el_animated.findall('.//waypoint'):
			if idx == 0:
				wp.set('time','-4.8s')
				replace(wp,el_base)

			else:
				if wp.get('time') != "-2s":
					time = wp.get('time')
					timef = float(time.strip("s"))+2.4
					timef = round(timef, 3)
					wp.set('time',str(timef)+'s')
					val_r_new = float(wp[0].get('value'))+val_r_awal
					wp[0].set('value',str(val_r_new))

			idx +=1

def get_id_shapekey(el_link):

	el_id_shapekey = el_link.find(".//timeloop/link_time//link/map_range/link/") # awal
	#el_id_shapekey = el_link.find(".//timeloop/link_time//to_max/map_range/link/")
	return el_id_shapekey.get('guid')

def set_controller_toeditmode(el_add,el_entrytime):

		print('[.] Controller to editmode')
		#BUAT bone conroller menjadi animasi, cukup sekali
		el_link_value = el_entrytime.find('.//to_max/map_range/link/')
		el_from_min = el_entrytime.find('.//to_max/map_range/from_min/')
		el_from_max = el_entrytime.find('.//to_max/map_range/from_max/')
		varglo.sudut_min = el_from_min.get('value') # get isi buat bone
		varglo.sudut_max = el_from_max.get('value')

		if el_link_value.tag in ['animated','real']:
			varglo.id_edit_sub_smartkey=el_link_value.get('guid')

			value_sud = copy.deepcopy(el_link_value)
			value_sud.attrib.pop('guid')
			set_controllertomode_editz(el_add,varglo.id_edit_sub_smartkey,value_sud)

		if el_link_value.tag == 'vectorlength': # dari IK manual
			varglo.type_controller = 'ik'
			varglo.jenis_ik = 'ikmanual'
			el_target = el_link_value.find('.//lhs/add')
			varglo.id_edit_sub_smartkey = el_target.get('guid')
			value_sud = 'o'
			set_controllertomode_editz(el_add,varglo.id_edit_sub_smartkey,value_sud)	

		print('[..] done')

def apa_terkoneksi(el_add,id_shapekey,el_defs):

	terkonek = False
	guid_target = None
	type_value = ''
	el_animated = None
	
	for el_entrytime in el_add.findall(".//timeloop/.."):
		id_sk = get_id_shapekey(el_entrytime)
	
		if id_sk == id_shapekey:
			el_animated = el_entrytime.find('.//link/animated')
			type_value = el_animated.get('type')
			guid_this = str(uuid.uuid4())
			ganti_animasi_keawal(el_animated)
			el_animated.set('guid',guid_this)
			
			el_cont = el_entrytime.find('.//map_range/link/') # gak di pake??

			if varglo.id_edit_sub_smartkey == None: 
				set_controller_toeditmode(el_add,el_entrytime) #di perbaiki

	if 	el_animated == None:
		if el_add[0].tag == 'add':
			#if 'guid' in el_add[0].attrib:
				#if el_add[0].get('guid') != varglo.id_controller:
			export_todefs(el_add,el_defs)

	else:
		
		varglo.valueattime_elcounter +=1
		idname = ''
		guid_this = None
		#if 'influence' in el_add.attrib:
			#el_add.attrib.pop('influence')
			#idname = 'inf_'
			#guid_this = el_add[0].get('guid')

		idname += 'shapekey_'+str(varglo.valueattime_elcounter)
		el_tobe_export = copy.deepcopy(el_add[0])
		el_tobe_export.set('id',idname)
		#el_defs = get_defs()
		el_defs.append(el_tobe_export)
		replace(el_add,el_animated)

		if guid_this != None:
			for el_this in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
				if el_this.tag != 'defs':
					replace(el_this,el_animated)

	#	print('[..] done')

def del_onoff_key(el_valueattime):

	if 'on' in el_valueattime.attrib:
		el_valueattime.attrib.pop('on')

	if 'off' in el_valueattime.attrib:
		el_valueattime.attrib.pop('off')

def cek_parent_loop(el_add):

	el_add_parent = get_parent(el_add,1)
	
	if el_add_parent != None:
		if el_add_parent.tag in ['vectorlength','map_range']:
			return 'NO'
		else:
			#if el_add_parent.tag == 'average':
				#el_add.set('influence','data')

			return 'OK'

def erase_export_shapekeys():

	if len(varglo.data_error) >0:
		return

	el_defs = get_defs()

	remove_list = []
	for el_export in el_defs.findall(".//*[@id]"):
		if "shapekey_" in el_export.get('id'):
			remove_list.append(el_export)

	for el in remove_list:
		el_defs.remove(el)

def set_infcontroller(): #set back
	print("   set back inf")
	def convert_nonswitch(bone,entry):

		el_base = entry.find(".//link_off/")
		guid_this = el_base.get('guid')
		
		el_awal  = entry.find(".//link_on/")
		el_awal.set('guid',guid_this)
		el_awal_c = copy.deepcopy(el_awal)
		
		replace(entry,el_awal_c)

		el_realinf = bone.find(".//name/join//realstring/")
		if el_realinf != None:
			replace(el_realinf,el_awal_c)

		for el_inf in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
			
			if el_inf[0].tag != 'add':
				replace(el_inf,el_awal_c)

	el_bones = varglo.root_file.find(".//bones")
	for bone in el_bones.findall(".//bone"):
		for entry in bone.findall(".//scalex//average/entry"):
			if entry[0].tag == 'switch':
				convert_nonswitch(bone,entry)

def find_infcontroller():#set to switch data

	print("   >>> inf searching")
	def convert_switch(entry,tipe):
		guid_this = entry[0].get('guid')

		el_add = copy.deepcopy(entry[0])
		el_add.attrib.pop('guid')
		el_add.set('guid',str(uuid.uuid4()))
		
		el_awal = None
		if tipe == 'add':
			el_awal = el_add.find(".//rhs/")

		else:
			el_awal = el_add.find(".//waypoint/")

		el_awal_c = copy.deepcopy(el_awal)
		el_awal_c.set('guid',guid_this)

		el_switch = load_template(".//*[@kunci='SK_inf_switch']/")
		el_base = el_switch.find(".//link_off")
		replace(el_base,el_awal_c)
		el_base_add = el_switch.find(".//link_on")
		replace(el_base_add,el_add)
		replace(entry,el_switch) # set to switch

		for el_inf in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
			replace(el_inf,el_awal_c)

	el_bones = varglo.root_file.find(".//bones")
	for bone in el_bones.findall(".//bone"):
		for entry in bone.findall(".//scalex//average/entry"):
			if entry[0].tag == 'add':
				convert_switch(entry,'add')

			if entry[0].tag == 'animated':
				convert_switch(entry,'animated')
				
def find_controller_and_editkey():

	print('[.] searching timeloop')

	set_shapekey_aktif('no efek',True)
	el_defs = get_defs()

	for el_add in varglo.root_file.findall(".//add/lhs/add/../../.."):
		influence = False 

		if cek_parent_loop(el_add) == "OK":
			del_onoff_key(el_add)
			apa_terkoneksi(el_add, varglo.id_controller ,el_defs)

	print('[..] OK')

def create_list_shapekeys():

	if len(varglo.data_error)==0:
		parent_bone_cont= get_parent(varglo.bone_cont_layer,5)

		text_layer = load_template(".//*[@kunci='SK_text_shapekeys']")
		el_string = text_layer.find(".//param/string/..")
		replace(el_string,varglo.el_name_current_cont)
		rhs = text_layer.find(".//*[@guid='GUID_controller_pos']/..")
		replace(rhs,varglo.el_pos_controller)
		guid_inf = text_layer.find(".//*[@guid='GUID_toshapekeys']") # konektor
		guid_inf.set('guid',varglo.influence)
		parent_bone_cont.append(text_layer[0]) # now must in same layer bone

def set_name_bone(el_string,el_name_bone):

	name_akhir = el_string.text
	nama_controller = ''

	if varglo.nama_controller == 'none':
		nama_controller = 'shapekey_'+str(varglo.controller-1)

	else:
		nama_controller = varglo.nama_controller

	el_name_templ = None

	if el_name_bone[0].tag == 'greyed':
		el_name_templ = load_template(".//*[@kunci='SK_name_sk_bone']/")
		
		el_name_entry = el_name_templ.find(".//*[@guid='NAMA_SK']")
		el_name_entry.attrib.pop('guid')
		el_name_entry.text = nama_controller

		el_name_entry.set('guid',str(uuid.uuid4()))
		varglo.el_name_current_cont = copy.deepcopy(el_name_entry)

		el_after = el_name_templ.find(".//after/string")
		el_after.text = name_akhir

		el_inf = el_name_templ.find(".//*[@guid='INF_SK']/..")
		replace(el_inf,varglo.el_influence)

		varglo.nama_controller = el_name_entry.text

	else: # if joint text
		el_name_templ = el_name_bone[0]
		el_entry_up = el_name_templ.find(".//dynamic_list")
		el_entry_child = copy.deepcopy(el_entry_up[0]) # copy entry pertama string

		if 'guid' in el_entry_child[0].attrib:
			el_entry_child[0].attrib.pop('guid')

		el_string = el_entry_child.find(".//link_off/string")
		el_string.text = nama_controller
		el_string.set('guid',str(uuid.uuid4()))
		
		el_inf = el_entry_child.find(".//link_on/realstring/real")
		replace(el_inf,varglo.el_influence)

		varglo.el_name_current_cont = copy.deepcopy(el_string)

		el_after = el_name_templ.find(".//after")
		if el_after[0].tag =='greyed':
			el_string_this = copy.deepcopy(el_after[0][0][0])
			replace(el_after,el_string_this)

		el_entry_up.append(el_entry_child)

	varglo.el_name_bone = el_name_templ

def set_get_name_layercont(el,el_string,el_name_bone):

	guid_this = el.get('guid')
	for sk in varglo.root_file.findall(".//*[@type='skeleton']"):
		for el_sk in sk.findall(".//bone"):
			if el_sk.get('guid')==guid_this:
				varglo.bone_cont_layer = el_sk

				if 'desc' in sk.attrib:
					if 'New Controller' in sk.get('desc'):
						#if not 'Bone_controller_' in sk.get('desc'):
						sk.set('desc','Bone_controller_'+str(varglo.controller))
						print('   >>> create name controller')
						
					else:
						if 'Bone_' in sk.get('desc'):
							varglo.nama_controller = 'shapekey_'+str(varglo.controller-1)
						else:
							varglo.nama_controller = sk.get('desc')
					
				else:
					sk.set('desc','Bone_controller_'+str(varglo.controller))
					print('   >>> create name controller!')

				set_name_bone(el_string,el_name_bone)

def set_name_cont(el,el_string,el_name_bone):

	influence_data(el)
	get_totalcontroller('new cont')
	set_get_name_layercont(el,el_string,el_name_bone)
	
def cari_origin_base_bone():

	el_bones = varglo.root_file.find(".//bones")

	for bone in el_bones.findall(".//bone"):
		el_name = bone.find(".//name")
		
		if el_name == None: # in depth ada data bone aja sehingga tidak ada name
			continue

		el_string = el_name.find(".//reverse/link/string")
		if el_string != None:
			return bone

	return None

def converted_to_add(el_origin):

	el_animated_c = copy.deepcopy(el_origin[0])
	guid_this = None

	if 'guid' in el_animated_c.attrib:
		guid_this = el_animated_c.get('guid')
		el_animated_c.attrib.pop('guid')

	el_origin_t = load_template(".//*[@kunci='SK_origin_add']")
	el_lhs = el_origin_t.find(".//animated/..")

	if not guid_this == None:
		el_origin_t[0].set('guid',guid_this)


	replace(el_lhs,el_animated_c)
	replace(el_origin,el_origin_t[0])
				
def get_defs():

	el_defs =varglo.root_file.find(".//defs")
	if not el_defs== None:
		return el_defs

	else:
		el_defs = load_template(".//*[@kunci='SK_defs']")
		varglo.root_file.insert(0,el_defs[0])
		el_defs =varglo.root_file.find(".//defs")
		return el_defs

def get_setdata_sud(el_animasi_ik,el_vec_original):

		if el_animasi_ik == None:
			print('   !!! missing animated ik')
			varglo.data_error['bone ik animated']='missing'
			return

		for el_guid in el_animasi_ik.findall(".//*[@guid]"): # hapus guid di data animas
			el_guid.attrib.pop('guid')

		varglo.el_animasi_controller_bone = copy.deepcopy(el_animasi_ik)
		el_animasi_copy = copy.deepcopy(el_animasi_ik)

		x_base = float(el_vec_original[0].text)
		y_base = float(el_vec_original[1].text)

		el_wayp = el_animasi_copy.findall(".//waypoint")
		waypoint_banyaknya = len(el_wayp)

		vec_jauh = el_animasi_copy[waypoint_banyaknya-1][0] # vector akhir jika ada lebih dari 2
		vec_dekat  = el_animasi_copy[0][0] # vector awal
		x_selisihA = float(vec_dekat[0].text)-x_base 
		y_selisihA = float(vec_dekat[1].text)-y_base 

		varglo.sudutik_to_target = math.degrees(math.atan2(y_selisihA,x_selisihA))

		x_selisihB = float(vec_jauh[0].text)-x_base 
		y_selisihB = float(vec_jauh[1].text)-y_base 

		varglo.sudut_min = str(math.sqrt(x_selisihA*x_selisihA+y_selisihA*y_selisihA))
		varglo.sudut_max = str(math.sqrt(x_selisihB*x_selisihB+y_selisihB*y_selisihB))

def create_controller_ik(el_origin_target,el):

	selisih_time = get_selisih_time()
	#ET.dump(el_origin_target)
	if el_origin_target[0].tag == 'animated':

		converted_to_add(el_origin_target)
		bone = cari_origin_base_bone()
		if bone != None:
			el_origin_base = bone.find('.//origin')
			converted_to_add(el_origin_base)

	el_origin_base = None
	el_vec_original = None
	el_bone_depth_base = None
	el_bone_depth_target = None
	el_parent_base = None

	bones = varglo.root_file.find(".//bones")
	el_rootbone = bones.find(".//bone_root")
	guid_rootbone = el_rootbone.get('guid')

	missing_base_bone = True
	el_bone = bones.find('.//bone/name/reverse/link/../../..')

	if el_bone == None:
		varglo.data_error['bone base ik ']='missing'
		print('   !!! missing base bone ik/ code reverse not found')
		return

	el_name = el_bone.find('.//name')	
	el_bone.set('base','ik')
	el_string = el_name.find('.//string')	
	el_jenis = el_bone.find(".//angle/")
	varglo.type_controller = 'ik'

	if el_jenis.tag == 'ik':
		varglo.jenis_ik = 'ik_angle'
		el_bone.attrib.pop('base') # tidak perlu

	else:
		varglo.jenis_ik = 'ikmanual'
		if varglo.guid_flip == None: # create guid flip ik manuaal
			varglo.guid_flip = str(uuid.uuid4())

	el_name_copy = copy.deepcopy(el_string)

	if not 'base_cont' in el_name_copy.text:
		el_name_copy.text = el_name_copy.text+'@base_cont_ik'

	el_name_copy.set('static','true')
	varglo.controller_data.append([el_name,el_name_copy,"replace"])

	el_origin_base = el_bone.find(".//origin")
	el_vec_original = el_origin_base.find(".//lhs/vector")
	el_vec_original_new=copy.deepcopy(el_vec_original)

	if el_vec_original == None:
		el_an = el_origin_base.find(".//lhs/animated/..")

		if el_an != None:
			el_vec = el_an.find('.//vector')
			el_vec_original = copy.deepcopy(el_vec)
			replace(el_an,el_vec_original)

		else:
			el_vec_original = el_origin_base[0]

	else:
		pass # mungkin animasi bukan add, convert dulu 

	el_vec_original_lhs = el_origin_base.find(".//rhs//vector") # add pos

	if el_vec_original_lhs != None:
		x_lhs = float(el_vec_original[0].text)+float(el_vec_original_lhs[0].text)
		y_lhs = float(el_vec_original[1].text)+float(el_vec_original_lhs[1].text)

		el_vec_original_new[0].text = str(x_lhs)
		el_vec_original_new[1].text = str(y_lhs)

	el_bone_depth_base =  el_bone.find(".//bone_depth")
	el_parent_base = el_bone.find(".//parent/")

	if el_origin_base != None:
		el_animasi_ik = el_origin_target.find(".//animated")
		move_animasi_thiske_editmode(el_animasi_ik, False)
		
		#CREATE DATA ORIGIN FOR BASE:
		el_origin_base_c = copy.deepcopy(el_origin_base[0])
		get_setdata_sud(el_animasi_ik,el_vec_original_new)

		if 'guid' in el_origin_base_c.attrib:
			el_origin_base_c.attrib.pop('guid')

		else:
			new_guid = str(uuid.uuid4())
			el_origin_base[0].set('guid',new_guid)

		el_origin_base_t = load_template(".//*[@kunci='SK_origin_base_IK']")
		el_base_new = el_origin_base_t.find(".//*[@guid='ORIGIN_BASE']/..")
		replace(el_base_new,el_origin_base_c) # ISI ORIGIN SEBAGAO AWAL BASE VALUE
		replace(el_bone_depth_base,el_origin_base_t[0]) # ISI DEPTH BONE BASE DENGAN DATA DEPTH

		el_base_new = el_origin_base_t.find(".//*[@nama='BONEparent_base']/..") # DATA BONE PARENT
		replace(el_base_new,el_parent_base)

		#CREATE DATA ORIGIN FOR TARGET:
		el_depth_target = el.find(".//bone_depth")
		el_origin_target_t = load_template(".//*[@kunci='SK_origin_target_IK']")
		el_origin_target_c = copy.deepcopy(el_origin_target[0])

		if 'guid' in el_origin_target_c.attrib:
			el_origin_target_c.attrib.pop('guid')

		el_target_new = el_origin_target_t.find(".//*[@guid='ORIGIN_TARGET']/..")
		replace(el_target_new,el_origin_target_c)

		#replace(el_depth_target,el_origin_target_t[0]) # ISI DEPTH BONE BASE DENGAN DATA DEPTH
		varglo.controller_data.append([el_depth_target,el_origin_target_t[0],"replace"]) # ganti cara agar data awal target animaasi tidak menubah menjadi timeloop
		#create SK_angle_IK
		el_lhs = el_origin_target.find(".//lhs") # DATA FILE ORIGIN TARGET HARUS ADA CONVERT ADD
		el_lhs_vector = el_origin_target.find(".//lhs/animated/waypoint/vector")

		if varglo.user_animated_target != None:
			replace(el_lhs,varglo.user_animated_target)
		else:
			replace(el_lhs,el_lhs_vector)

		el_SK_angle_IK = load_template(".//*[@kunci='SK_angle_IK']")
		
		if el_SK_angle_IK != None:
			el_lhs_target = el_SK_angle_IK.find(".//*[@guid='ORIGIN_TARGET']/..")
			replace(el_lhs_target,el_origin_target[0])
			el_rhs_base = el_SK_angle_IK.find(".//*[@guid='ORIRIN_BASE']/..")
			replace(el_rhs_base,el_origin_base[0])

			varglo.el_angle_IK = el_SK_angle_IK[0] # untuk konektor ke bone ik masuk ke range map di timeloop
			# ganti semua original menjaadi non animasi
			guid_target = el_origin_target[0].get('guid')
			varglo.el_pos_controller = el_origin_target[0]

			if guid_target == None:
				new_guid = str(uuid.uuid4())
				el_origin_target[0].set('guid',new_guid)
			
			for el_ori in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no= guid_target)):
				if el_ori.tag == 'link_target':
					replace(el_ori,el_origin_target[0])
		else:
			print('   !!! missing template ik bone')
			varglo.data_error['ik template']= 'missing'
			return

	print('   +++ create ik controller done')

def set_static_bone(el_file, tipe):

	el_list_tag = []

	if tipe == 'bone':
		el_list_tag = [".//name/greyed/link/string",".//scalelx/real",".//width/",".//scalex/real",".//tipwidth/",".//length/",".//bone_depth/real",".//origin/vector",
		".//length_bone1/real",".//length_bone2/",".//length_bone3/",".//flip/",".//joint_bone/",".//t_bone/",".//f_bone/",".//weight/",".//parent/",".//angle/angle"
		]
	if tipe == 'rotate':
		el_list_tag = [".//param/vector"]

	if tipe == 'star':
		el_file.set('exclude_from_rendering','true')
		el_list_tag = [".//param/vector"]

	for el_tag in el_list_tag:
		el_ini = el_file.find(el_tag)
		if not el_ini == None:
			if not 'static' in el_ini.attrib:
				el_ini.set('static','true')
				#print("make static ",el_tag)

def get_sudutcontroller(el_an):

	idx = 0
	for el_sud in el_an.findall('.//real'):
		if idx == 0:
			varglo.sudut_min = el_sud.get('value')

		else:
			varglo.sudut_max = el_sud.get('value')

		idx +=1

def get_set_angle_maxmin(el_angle): #set varglo.sudut_min/varglo.sudut_max

	rhs = el_angle.find('.//rhs/animated')
	vec_base1 = None
	vec_base2 = None
	if rhs == None:
		vec_base1 = el_angle.find('.//rhs/vector')

	else:
		wp = rhs.findall(".//waypoint")
		if len(wp)>1:
			vec_base1 = wp[0][0]
			vec_base2 = wp[len(wp)-1][0]
		
	lhs = el_angle.find('.//lhs/animated')
	if not lhs == None:
		wp = lhs.findall(".//waypoint")
		if len(wp)>1:
			vec_target1 = wp[0][0]
			vec_target2 = wp[len(wp)-1][0]

			v1=[float(vec_target1[0].text),float(vec_target1[1].text)]
			v2=[float(vec_target2[0].text),float(vec_target2[1].text)]

			x_selisihA = float(vec_target1[0].text)-float(vec_base1[0].text) 
			y_selisihA = float(vec_target1[1].text)-float(vec_base1[1].text) 
			varglo.sudut_min = str(math.degrees(math.atan2(y_selisihA,x_selisihA)))

			x_selisihB = float(vec_target2[0].text)-float(vec_base1[0].text) 
			y_selisihB = float(vec_target2[1].text)-float(vec_base1[1].text) 

			varglo.sudut_max =str(math.degrees(math.atan2(y_selisihB,x_selisihB)))

def create_elvectorangle(el_angle):

	guid_controller_angle = str(uuid.uuid4())
	el_angle_template = load_template(".//*[@kunci='SK_angle2point']")

	vec_target_temp = el_angle.find(".//animated/waypoint/")
	vec_target = copy.deepcopy(vec_target_temp)
	vec_target.set('guid',varglo.id)
	vec_base_temp = el_angle.find(".//rhs")
	vec_base = copy.deepcopy(vec_base_temp[0])

	#replace 
	lhs = el_angle_template.find(".//*[@guid='TARGET_to']/..")
	replace(lhs,vec_target)
	rhs = el_angle_template.find(".//*[@guid='BASE_thisbone']/..")
	replace(rhs,vec_base)
	guid_angle = el_angle_template.find(".//*[@guid='GUID_angle']")
	guid_angle.set('guid',guid_controller_angle)

	get_set_angle_maxmin(el_angle)
	replace(el_angle,el_angle_template[0])
	varglo.el_controller_bone = guid_angle

	for el_sub in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = varglo.id)):
		replace(el_sub,vec_target)

def set_el_pos_controller(el):

	el_ori = el.find(".//origin")

	if 'guid' in el_ori[0].attrib:
		pass
	else:
		el_ori[0].set('guid',str(uuid.uuid4()))

	varglo.el_pos_controller = el_ori[0]

def create_controller_lenght(el_lenght,el):

	el_wps = el_lenght.findall(".//waypoint")
	el_animated = el_lenght.find(".//animated")

	if len(el_wps)>=2:
		varglo.sudut_min = el_wps[0][0].get('value')
		varglo.sudut_max = el_wps[1][0].get('value')

		el_lenght_new = copy.deepcopy(el_wps[0][0])

		if 'guid' in el_animated.attrib: # sudah ada guid
			varglo.id = el_animated.get('guid')
			el_animated.attrib.pop('guid') # hapus guidnya

		el_lenght_new.set('guid',varglo.id)
		set_el_pos_controller(el)
		replace(el_lenght,el_lenght_new)

		varglo.el_controller_bone = el_lenght[0]
		varglo.type_controller = 'length'

	else:
		print(" !!! missing waypoint controller")
		varglo.data_error['waypoint length']="missing"

def create_controller_angle(el_angle,el):

	set_el_pos_controller(el)

	el_an = el_angle.find(".//animated")
	if el_an == None:
		print("   !!! Missing animated bone controller")
		varglo.data_error['bone_key']="missing"
		return

	if 'guid' in el_an.attrib: # sudah ada guid
		varglo.id = el_an.get('guid')
		el_an.attrib.pop('guid') # hapus guidnya

	wps = el_an.findall(".//waypoint")
	if len(wps)==1:
		print("   !!! controller need minimal two waypoints ")
		varglo.data_error['bone_key']="missing waypoint"
		return

	el_value = None
	sudah_jadi_controller = False

	if el_angle[0].tag == 'animated':
		el_value = el_an.find(".//angle")
	else: # jika sudah dibuat controller
		if el_angle[0].tag == 'vectorangle':
			varglo.type_controller = 'vectorangle'
			varglo.vectorangle = True
			create_elvectorangle(el_angle)
			return
		else:
			varglo.type_controller = 'angle'
			sudah_jadi_controller = True
			el_value = el_an.find(".//real")

	el_value_copy = copy.deepcopy(el_value)
	el_value_copy.set('guid',varglo.id)
	el_value_copy.tag = 'real'
	varglo.el_controller_bone = el_value_copy

	#jika tidak ada maka ambil langsung setiap kali plugin  jalan maka akan membuat id
	#ganti animated menjadi real value
	if not sudah_jadi_controller:
		el_an.set('type','real')
		for el_a in el_an.findall('.//angle'):
			el_a.tag = 'real'
	#convert dulu menjadi from angle to real
		el_toreal = load_template(".//*[@kunci='SK_toreal']")
		el_real = el_toreal.find('.//real/..')

		replace(el_real,el_value_copy)
		replace(el_angle,el_toreal[0])

	else:
		el_link = el_angle.find('.//link')
		replace(el_link,el_value_copy)

	varglo.el_animasi_controller_bone = copy.deepcopy(el_an)
	get_sudutcontroller(el_an)

	if varglo.id_edit_sub_smartkey == None:
		varglo.id_edit_sub_smartkey = str(uuid.uuid4())

	print("   >>> create controller angle done")

def bone_inlayer(el):

	guid_this = el.get('guid')

	if len(varglo.list_skeleton)== 0:
		varglo.list_skeleton = varglo.root_file.findall(".//*[@type='skeleton']")

	for layer_skeleton in varglo.list_skeleton:
		layer = layer_skeleton.find(".//*/[@guid='{no}']/..".format(no = guid_this))
		if not layer == None:
			return True

		else:
			continue

	return False

def delete_angleani(el_angle):

	guid_this = None
	if 'guid' in el_angle[0].attrib:
		guid_this = el_angle[0].get('guid')

	el_angle_ani = el_angle.find(".//angle")
	if el_angle_ani != None:
		el_angle_c = copy.deepcopy(el_angle_ani)

		if guid_this != None:
			el_angle_c.set('guid',guid_this)

		else:
			if 'guid' in el_angle_c.attrib:
				el_angle_c.attrib.pop('guid')

		replace(el_angle,el_angle_c)

def set_grayed_bone(el):

	el_grey = load_template(".//*[@kunci='SK_greykode']/")

	el_after_val = None
	el_after = el.find(".//name/join/after")
	if el_after != None:
		el_after_val = copy.deepcopy(el_after[0])
	else:# jika baru bnget/ hati 2 jik ada 2 bone ada animasi yang sama di anglenya
		el_after = el.find(".//name")
		el_after_val = copy.deepcopy(el_after[0])

	replace(el_grey[0],el_after_val)
	replace(el_after,el_grey)


def do_greyed(el_angle,el):

	wp_time = el_angle.get('time')
	if wp_time == '-4.80000019s':
		set_grayed_bone(el)

def get_bone_list(list_angle_ani):

	list_bone = []
	for bone in list_angle_ani:
		el_bone = get_parent(bone,2)
		if el_bone.tag == 'bone':
			guid_this = el_bone.get('guid')
			el_name = el_bone.find(".//name/")
			name_bone = None

			if el_name.tag == 'string':
				name_bone = el_name.text

			else:
				el_nm = el_name.find(".//after/")
				name_bone = el_nm.text

			list_bone.append([name_bone,guid_this,el_bone])

	return list_bone

def find_bone_with_ani(el):

	from GTKtools import select_bone

	el_bones = varglo.root_file.find(".//bones")
	el_angle_ani = el_bones.findall(".//angle//animated")
	el_scalelx_ani = el_bones.findall(".//scalelx//animated")

	done_greyed = False
	if len(el_scalelx_ani)== 0:

		if len(el_angle_ani)>1:

			count_angl = 0
			for el_ang in el_angle_ani:
				el_up = get_parent(el_ang,1)
				if el_up.tag in ['link','angle']:
					count_angl +=1

			if count_angl >1:
				el_bone = select_bone(get_bone_list(el_angle_ani))
				set_grayed_bone(el_bone)
				done_greyed = True
	else:
		if len(el_scalelx_ani)>1:
			el_bone = select_bone(get_bone_list(el_scalelx_ani))
			set_grayed_bone(el_bone)
			done_greyed = True

	if not done_greyed: 
		el_lenght = el.find(".//scalelx//animated/")

		if el_lenght != None:
			do_greyed(el_lenght,el)

		else:
			el_angle = el.find(".//angle//animated/")
			if el_angle != None:
				el_up = get_parent(el_angle,1)
				if el_up.tag in ['link','angle']:
					if el_angle != None:
						do_greyed(el_angle,el)

def buat_controller():

	from GTKtools import show_message

	print(' ')
	print('[.] searching controller ')

	type = [".//bone[@type='bone_object']"]#,".//*[@type='star']",".//*[@type='rotate']",".//*[@type='text']"]
	missing_target_bone = True

	for i in [0]:
		if varglo.id_edit_sub_smartkey != None:
			return
			
		cari_el = varglo.root_file.findall(type[i])
		for el in cari_el:

			if varglo.id_edit_sub_smartkey == None:
				if i==0:
					el_name = el.find(".//name")

					if not el_name == None:
						el_string = el_name.find(".//greyed/link/string/../../..")  # khusus smartkey bone layer or convert to greyed


						if bone_inlayer(el):
							#if el_string == None: # 
								#jika ada 2 bone animasi angle?? mapa perlu show seleck by GTK
								#find_bone_with_ani(el) # auto greyed untuk angle dan lenght. untuk ik wajib
								#el_string = el_name.find(".//greyed/link/string/../../..") 

							if el_string != None:
								if missing_target_bone:
									missing_target_bone = False

								el_name_copy = copy.deepcopy(el_string[0][0][0])
								if not 'shapekey_' in el_name_copy.text:
									el_name_copy.text = '@shapekey_cont'


								el_name_copy.set('static','true')
								set_name_cont(el,el_name_copy,el_name) # layer
								el_origin_file = el.find(".//origin")


								if el_origin_file[0].tag == 'add':
									varglo.ik_smartkey = True
									set_static_bone(el,'bone')
									create_controller_ik(el_origin_file,el)
									print('[..] IK angle controller')
									el_string_this = varglo.el_name_bone.find(".//after/string")
									el_string_this.text = el_string_this.text +'_ik'
									varglo.controller_data.append([el_name,varglo.el_name_bone,"replace"])
									#create_smart_ik_controller(el_origin_file,el ) #CANCEL FROM IK FORMULA//ik plugin
									return 

								else:

									el_sud = el.find(".//angle/animated")
									if el_origin_file[0].tag == 'animated'and el_sud == None :
										varglo.ik_smartkey = True
										set_static_bone(el,'bone')
										create_controller_ik(el_origin_file,el)
										print('[..] ik controller')
										el_string_this = varglo.el_name_bone.find(".//after/string")
										el_string_this.text = el_string_this.text +'_ik'
										varglo.controller_data.append([el_name,varglo.el_name_bone,"replace"])
										return

									else:
										el_lenght = el.find(".//scalelx/animated/..")
										if not el_lenght == None:
											el_angle = el.find(".//angle/animated/..")

											if el_angle != None: # del animated
												delete_angleani(el_angle)

											set_static_bone(el,'bone')
											create_controller_lenght(el_lenght,el)
											print('[..] length controller')
											el_string_this = varglo.el_name_bone.find(".//after/string")
											el_string_this.text = el_string_this.text +'_lenght'
											varglo.controller_data.append([el_name,varglo.el_name_bone,"replace"])
											print('[..] done')
											return
										else:
											el_angle = el.find(".//angle")	
											set_static_bone(el,'bone')
											create_controller_angle(el_angle,el) # for angle controler/ vectorangle need animasi target

											varglo.controller_data.append([el_name,varglo.el_name_bone,"replace"])
											print('[..] done')
											return

							
	if missing_target_bone:
		print('    !!! bone missing / missing controller/ code greyed not found')
		#show_message("!!! bone missing / missing controller/ code greyed not found")

	print('[..]')

	varglo.data_error['bone controller']='missing'
	return

def split_bline():

	print("    >>> split set")
	for el_bline in varglo.root_file.findall(".//bline"):
		for el_boolup in el_bline.findall(".//bool/.."):

			if el_boolup.tag == 'split':
				el_boolup[0].set('value','false')

			if el_boolup.tag == 'split_radius':
				el_boolup[0].set('value','true')

			if el_boolup.tag == 'split_angle':
				el_boolup[0].set('value','false')

def export_todefs(el_add, el_defs):

	guid_this = str(uuid.uuid4())

	varglo.valueattime_elcounter +=1
	idname = ''
	#if influence:
		#idname +='inf_'

	idname += 'shapekey_'+str(varglo.valueattime_elcounter)
	el_tobe_export = copy.deepcopy(el_add[0])

	#ET.dump(el_tobe_export)
	el_tobe_export.set('id',idname)
	el_defs.append(el_tobe_export)
	#varglo.controller_data.append([el_defs,el_tobe_export,"append"])
	el_rhs = el_tobe_export.find('.//lhs/add/rhs')

	el_rhs[0].set('guid',guid_this)
	#varglo.valueattime_list.append([el_add,el_rhs[0]])
	#if influence:
		#guid_this = el_tobe_export.get('guid')

		#for el_this in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no=guid_this)):
			#if el_this.tag == 'link':

				#replace(el_this,el_rhs[0])

	replace(el_add,el_rhs[0])

def set_nulreal(el_real):

	if 'guid' in el_real.attrib:
		el_real.attrib.pop('guid')

	el_real.set('value','0')

def set_nulpos(vector):

	if 'guid' in vector.attrib:
		vector.attrib.pop('guid')

	vector[0].text = '0'
	vector[1].text = '0'

def convert_tonewADD(el_add):

	el_tobe_export = el_add[0]
	el_rhs = el_tobe_export.find('.//lhs/add/rhs')
	el_tobe_active = copy.deepcopy(el_rhs)

	if 'guid' in el_tobe_active[0].attrib:
		el_tobe_active[0].attrib.pop('guid')

	el_active = el_tobe_export.find('.//link')

	if el_rhs[0].tag == 'vector':
		set_nulpos(el_rhs[0])

	else:
		set_nulreal(el_rhs[0])
		
	replace(el_active,el_tobe_active[0])
	# set skalar  1 and 0
	el_skala = el_tobe_export.find('.//scalar/')
	el_skala.set('value','1')

	el_skala2 = el_tobe_export.find('.//rhs/scale/scalar/')
	el_skala2.set('value','0')

def change_timeloop_to_basevalue():

	print(' ')
	print('[.] move timeloop to defs')

	split_bline()
	el_defs = get_defs()

	for el_add in varglo.root_file.findall(".//add/lhs/add/../../.."):
		sudah_didefs = False
		if cek_parent_loop(el_add) == "OK": # cek influence or not
			for el_entrytime in el_add.findall(".//timeloop/.."):

				if not sudah_didefs:
					sudah_didefs = True
					export_todefs(el_add,el_defs) #  model export data

	print('[..] OK')
		

	
def append_timeloop():

	if len(varglo.data_error) >0:
		return

	isi_influence = None

	for val in varglo.valueattime_list:
		val[0].append(val[1])

	


def influence_data(bone):

	print('   >>> create data influence')

	if varglo.influence == None:
		varglo.influence = str(uuid.uuid4())

	el_sc = bone.find('.//scalex')

	if el_sc[0].tag == 'switch':
		el_average = el_sc.find('.//link_on/average')

		if len(el_average)==0:
			
			parent_average = get_parent(el_average,1)
			el_average = load_template(".//*[@kunci='SK_AVERAGE']/")
			el_entry = el_average.find(".//entry")
			replace(parent_average,el_average)
			
		else:
			el_entry = copy.deepcopy(el_average[0])
			el_average.append(el_entry)

		el_entry[0].set('guid',varglo.influence)
		el_entry[0].set('value','100.0')
		varglo.el_influence = copy.deepcopy(el_entry[0])

	else:
		el_influence = load_template(".//*[@kunci='SK_influence']")
		el_val = el_influence.find('.//entry/real')
		el_val.set('guid',varglo.influence)
		replace(el_sc,el_influence[0])
		varglo.el_influence = el_val

def cari_guid_influence(bone):

	el_entry = bone.findall(".//scalex//average/entry")
	if len(el_entry) >1:
		print("   >>> found morethan 2 influence")

	if 'guid' in el_entry[0][0].attrib:
		print("   >>> make guid influence")
		return el_entry[0][0].get('guid')

def cek_error():

	error = False
	for er in varglo.data_error:
		if varglo.data_error[er]== 'missing':
			print(" found error in :",er,varglo.data_error[er])
			error = True

	if error:
		varglo.root_file = varglo.raw_file
		return

def reverse_to_normal(el_bone):

	bone_cont = el_bone.find(".//name/reverse/..")

	if bone_cont != None:
		el_string = bone_cont.find(".//string")
		copy_el_string =copy.deepcopy(el_string)
		replace(bone_cont,el_string)

def reference_to_normal(el_bone):

	bone_cont = el_bone.find(".//name//reference/..")

	if bone_cont != None:
		el_string = bone_cont.find(".//string")
		copy_el_string =copy.deepcopy(el_string)
		replace(bone_cont,copy_el_string)

def find_bone_baseik():

	el_bones = varglo.root_file.find(".//bones")
	el_bonebase = el_bones.find(".//name/reverse/../..")

	if el_bonebase != None:
		return el_bonebase

	else:
		varglo.data_error.append['missing base ik']='missing'
		print('missing bone base ik')
		return None

def get_originbase(bone_base):

	el_vector_base = bone_base.find('.//origin/add/lhs/vector')
	base_rhs = bone_base.find(".//origin/add/rhs/vector")
	
	if el_vector_base == None or base_rhs == None:
		el_vec_original = el_vector_base
		el_vec_original_new = copy.deepcopy(el_vec_original)
		el_vec_original_lhs = bone_base.find(".//origin/add/rhs//vector")

		x_lhs = float(el_vec_original[0].text)+float(el_vec_original_lhs[0].text)
		y_lhs = float(el_vec_original[1].text)+float(el_vec_original_lhs[1].text)

		el_vec_original_new[0].text = str(x_lhs)
		el_vec_original_new[1].text = str(y_lhs)
		
		return el_vec_original_new
	else:
		return el_vector_base

def get_el_angle_IK(bone_base):

	el_vector_lenght = bone_base.find('.//angle//vectorangle/..')
	if el_vector_lenght != None:
		el_this = copy.deepcopy(el_vector_lenght[0])
		el_this.tag == 'vectorlength'
		el_this.set('type','real')
		return el_this

	else: 
		return None

def update_sudut_min_max():

	el_defs = get_defs()
	for el_entrytime in el_defs.findall('.//timeloop/..'):
			
		id_shapekey = get_id_shapekey(el_entrytime) # jadi scalar
		
		if varglo.id_controller == id_shapekey:
			el_entrytime.set('shapekey','ok')
			el_sud_min = el_entrytime.find('.//link_time//to_max/map_range/from_min/')
			el_sud_max = el_entrytime.find('.//link_time//to_max/map_range/from_max/')

			el_sud_min.set('value',varglo.sudut_min)
			el_sud_max.set('value',varglo.sudut_max)

def set_back_origin(bone_base):

	el_origin_base = bone_base.find('.//origin')
	guid_this = el_origin_base[0].get('guid')
	el_origin_base[0].attrib.pop('guid')

	el_origin_edit = copy.deepcopy(el_origin_base[0])
	el_origin_basedepth = bone_base.find('.//bone_depth//vectorlength/vector')
	el_origin_basedepth[0].set('guid',guid_this)

	el_origin_basedepth_c = copy.deepcopy(el_origin_basedepth[0])
	replace(el_origin_basedepth,el_origin_edit)

	varglo.controller_data.append([el_origin_base,el_origin_basedepth_c,'replace'])

	for el_this in  varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
		replace(el_this,el_origin_basedepth_c)

def get_link_bone(guid_this):

	el_defs = get_defs()

	for el_this in  el_defs.findall(".//*/[@guid='{no}']/../../../..".format(no = guid_this)):
		if el_this.tag == 'vectorlength':
			return el_this

	return None

def get_jenis_ik (bone_base):

	el_this = bone_base.find('.//angle/ik')
	if el_this != None:
		return 'ik_angle'

	else:
		return 'ikmanual'

def update(el_ani,el_link):

	if el_ani != None:
		get_sudutcontroller(el_ani)
		guid_this = el_link[0].get('guid')

		el_linkon = el_link.find('.//link_on')
		el_baru = copy.deepcopy(el_linkon[0])
		el_baru.set('guid',guid_this)
		varglo.el_controller_bone = el_baru
		
		for el_sud in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
			replace(el_sud,el_baru)

		#UPDATE SEMUA SUDUT MIN MAX:
		el_defs = get_defs()

		for el_entrytime in el_defs.findall('.//timeloop/..'):
			shapekey_id = get_id_shapekey(el_entrytime) # jadi scalar
			
			if varglo.id_controller == shapekey_id:
				el_entrytime.set('shapekey','ok') # for active shape key in edit mode code
				el_sud_min = el_entrytime.find('.//link_time//to_max/map_range/from_min/')
				el_sud_max = el_entrytime.find('.//link_time//to_max/map_range/from_max/')
				el_sud_min.set('value',varglo.sudut_min)
				el_sud_max.set('value',varglo.sudut_max)
				el_influence = el_entrytime.find('.//map_range/link/')

				if varglo.influence == None: #GET GUID INFLUENCE
					varglo.influence = el_influence.get('guid')
	else:
		print("missing animated key controller")

def set_get_controller_active():

	print('[.] update controller')

	get_shapekey_list()
	get_totalcontroller('editmode')

	bone_controller = None 
	bones = varglo.root_file.find(".//bones")

	for el_bone in bones.findall(".//bone"):
		el_ref = el_bone.find(".//name//reference")

		if not el_ref == None:
			reference_to_normal(el_bone)
			bone_controller = el_bone
			el_link = el_bone.find('.//angle/fromreal/link/switch/..')

			if el_link != None:
				el_ani = el_link.find('.//animated')
				update(el_ani,el_link)
				
			else:
				el_scalex = el_bone.find(".//scalelx/switch/..")

				if not el_scalex == None:
					el_ani = el_scalex.find('.//animated')
					update(el_ani,el_scalex)

				else:
					varglo.influence = cari_guid_influence(el_bone)
					bone_base = find_bone_baseik()
					reverse_to_normal(bone_base)
					varglo.jenis_ik = get_jenis_ik (bone_base)
					
					if bone_base != None:
						pass

					el_vec_original = get_originbase(bone_base)
					set_back_origin(bone_base)

					varglo.el_angle_IK = get_el_angle_IK(bone_base)
					origin_target = el_bone.find('.//origin')
					guid_this = origin_target[0].get('guid')

					origin_target[0].attrib.pop('guid')
					el_animasi_ik = origin_target[0].find(".//animated")
					origin_target_awal = copy.deepcopy(origin_target[0])

					move_animasi_thiske_editmode(origin_target_awal, False)
					get_setdata_sud(el_animasi_ik,el_vec_original)
					update_sudut_min_max()

					if varglo.el_angle_IK == None:
						varglo.el_angle_IK = get_link_bone(guid_this)

					ani_temp = el_bone.find('.//bone_depth//vectorlength/')

					el_target_animasi_original = copy.deepcopy(ani_temp[0])
					el_target_animasi_original.set('guid',guid_this)
					replace(origin_target,el_target_animasi_original)
					#varglo.controller_data.append([ani_temp,origin_target_awal,'replace'])
					replace(ani_temp,origin_target_awal)

					for el_sud in  varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no = guid_this)):
						replace(el_sud,el_target_animasi_original)

	return bone_controller

def hide_animated_controllerik():

	el_bones = varglo.root_file.find(".//bones")

	if el_bones != None:
		for el_depth in el_bones.findall('.//bone_depth/switch/..'):
			if el_depth != None:
				el_animated = el_depth.find('.//animated')
				if el_animated != None:
					isi_this = copy.deepcopy(el_depth[0])
					el_depth.remove(el_depth[0])
					varglo.valueattime_list.append([el_depth,isi_this])

def turn_on_basic_keyframes(time):

	el_keyframe_this = varglo.root_file.find(".//keyframe[@time='{no}']".format(no= time))
	if el_keyframe_this != None:
		el_keyframe_this.set('active','true')

def set_time_leftright():
	
	varglo.time_left = varglo.input_areatime/varglo.fps
	varglo.time_right = (varglo.input_areatime+varglo.length_time)/varglo.fps

def del_name_sk(guid_name_sk):

	for el_layer_text in varglo.root_file.findall(".//*/[@guid='{no}']/../..".format(no= guid_name_sk)):
		if el_layer_text != None:
			if el_layer_text.get('type')== 'text':
				parent_text = get_parent(el_layer_text,1)
				parent_text.remove(el_layer_text)

def erase_shapekeys_in_layer(guid_this):

	for el_average in varglo.root_file.findall(".//average/entry/timeloop/../.."):
		for entry in el_average.findall(".//entry"):
			el_inf = entry.find(".//map_range/link/")

			if guid_this == el_inf.get('guid'):
				entrys = el_average.findall(".//entry")
				singel_sk = True

				if len(entrys) > 1:
					singel_sk = False
					el_average.remove(entry)
					#REDUCE DIV AVERAGE
					el_scale = get_parent(el_average,2)
					el_total_sk = el_scale[1][0]
					
					total_cont = float(el_total_sk.get('value'))
					total_cont -=1
					el_total_sk.set('value',str(total_cont))

				else:
					el_main = get_parent(el_average,5)
					el_rhs = el_main.find(".//add/lhs/add/rhs")
					if 'guid' in el_rhs[0].attrib:
						el_rhs[0].attrib.pop('guid')

					copy_el_rhs = copy.deepcopy(el_rhs[0])
					replace(el_main,copy_el_rhs)

def reduce_shapekey_count():

	total_cont = varglo.root_file.find(".//*[@name='shapekey_count']")
	total_sk = int(float(total_cont.get('content'))-1)
	total_cont.set('content',str(total_sk))

def del_shapekey(id_sk,name):

	bones = varglo.root_file.find(".//bones")
	el_controller_bones = bones.findall('.//scalex/switch//link_on/average/entry')
	data_namebone = []

	for entry in el_controller_bones:
		guid_this = entry[0].get('guid')
		layer_bone_this = get_parent(entry,5)

		if guid_this == id_sk:# remove antry in bone id sk/ remove influence / not if influence connect to shapekey
			average = get_parent(entry,1)

			if len(average) >1:# hapus entry tertentu
				average.remove(entry)

			else: # ganti ke kondisi awal
				el_scalex = get_parent(average,3)
				el_val = el_scalex.find(".//link_off/")
				replace(el_scalex,el_val)

			el_dynamic_list = layer_bone_this.find('.//name/join//dynamic_list')
			entrys = el_dynamic_list.findall(".//entry")
			single_sk = True

			if len(entrys)>1:
				single_sk = False

			for entry_tx in entrys:
				el_id = entry_tx.find(".//link_on/realstring/real/")
				guid_sk = el_id.get('guid')

				if id_sk == guid_sk:
					el_str = entry_tx.find(".//link_off/string")
					guid_name_sk = el_str.get('guid')
					del_name_sk(guid_name_sk) 

					if single_sk:
						el_bone_name = copy.deepcopy(el_str)
						el_bone_name.attrib.pop('guid')
						el_bone_name.text = 'Bone'
						el_namebone= layer_bone_this.find('.//name')
						replace(el_namebone,el_bone_name)

					else:
						el_dynamic_list.remove(entry_tx) # remove only one

	erase_shapekeys_in_layer(id_sk)
	reduce_shapekey_count()

def is_shapekey_deleted(apa):

	if apa == 'edit':
		if len (varglo.shapekey_rename_list) == 0:
			return apa

		else:
			for id_sk, name, newname in varglo.shapekey_rename_list:
				if newname == 'deleted':
					varglo.delete_shapekey = True
					print(">>> found deleted shapekey <<<")
					if id_sk == varglo.id_controller:
						apa = None

					del_shapekey(id_sk,name)

			return apa

	else:
		return apa

def get_set_mode():

	def process_editornewsmartkey(meta_mode,apa):

		if apa == None: # jika user cancel atau  tidak milih apapun
			varglo.mode_smartkey = 'None'

			if varglo.delete_shapekey:
				print(">>>Delete shapekey done<<<")
			else: 
				print("Exit shapekey nothing to do!!")

		else:
			if apa in ['merge','undo','clone','frezze']:
				print("   >>> "+apa+" Done")
				varglo.mode_smartkey = 'None'
				return

			if apa == 'edit':
				varglo.mode_smartkey = 'editmode'
				if meta_mode != None:
					meta_mode.set('content','editmode')

			else:
				set_time_leftright()
				varglo.mode_smartkey = 'inputkey'
				if meta_mode != None:
					meta_mode.set('content','inputkey')

	meta_mode = varglo.root_file.find(".//*[@name='shapekey_mode']")

	if meta_mode == None:
		apa = cari_smartkey(True)

		if apa == None or apa in  ['merge','undo','clone','delete']:
			varglo.mode_smartkey = 'None'
			return

		varglo.mode_before = 'begin'
		add_metamenu('shapekey_mode','inputkey')
		process_editornewsmartkey(meta_mode,apa) # true artiny awal bngat file sif/ atau tidak ada smartkey layer
		return

	else:
		if meta_mode.get('content') == 'editmode':
			meta_mode.set('content','play')
			varglo.mode_smartkey = 'play'
			varglo.mode_before = 'editmode'
			return

		if meta_mode.get('content') == 'play':
			apa = cari_smartkey(False) # GTK menu

			if len(varglo.smartkey_list)== 0 and meta_mode != None:# jika di awal gagal tidak ada controller setting ulang lagi seperti awal
				apa = cari_smartkey(True)

			apa = is_shapekey_deleted(apa)
			process_editornewsmartkey(meta_mode,apa) # False berarti bukan awal banget., sudah ada smartkey
			varglo.mode_before = 'play'
			return

		if meta_mode.get('content') == 'inputkey':
			meta_mode.set('content','play')
			varglo.mode_smartkey = 'play'
			varglo.mode_before = 'inputkey'
			return

def show_info(jenis):

	el_INFO_temporary = varglo.root_file.find(".//*[@desc='INFO_temporary']")

	if jenis in ['noedit','None']:
		if el_INFO_temporary != None:
			varglo.root_file.remove(el_INFO_temporary)

		return

	if el_INFO_temporary == None:
		el_info = load_template(".//*[@kunci='SK2_infosmartkey']")

		if jenis =='inputkey':
			el_text =  el_info.find(".//layer[@type='text']")
			el_text.set('desc', 'input key')
			el_string =  el_text.find(".//param/string")
			el_string.text = 'create shapekey'
			el_rectangle =  el_info.find(".//layer[@type='rectangle']")
			el_color =  el_rectangle.find(".//param/composite")
			el_color[0][0].set('value','0.0')
			el_color[1][0].set('value','0.1430629194')
			el_color[2][0].set('value','1.0')
			el_color[3][0].set('value','1.0')
			varglo.root_file.append(el_info[0])

		else:
			varglo.root_file.append(el_info[0])

def set_range_beginandendtime(mode):

	show_info(mode)

	if mode == 'edit':
		endtime = varglo.root_file.get('end-time')
		if endtime != None:
			endtime = varglo.edit_areatime+varglo.length_time

		varglo.root_file.set('begin-time',str(varglo.edit_areatime)+'f')
		varglo.root_file.set('end-time',str(endtime)+'f')

	elif mode == 'inputkey':
		endtime = varglo.root_file.get('end-time')
		meta = varglo.root_file.find(".//*[@name='end-time']")

		if meta == None:
			add_metamenu('end-time',endtime)
		else:
			meta.set('content',endtime)

		varglo.root_file.set('begin-time',str(varglo.input_areatime)+'f')

		if varglo.length_time > 99:
			varglo.length_time == 99

		endtime = varglo.input_areatime+varglo.length_time
		varglo.root_file.set('end-time',str(endtime)+'f') # ganti timeline posisi di -120 f : -70 f area input/edit

	else: # mode play/ normal balikan semua kondisi ke awal. timeline sesuai file sebelumnya
		temp = varglo.root_file.find(".//*[@name='end-time']")
		endtime=None

		if not temp== None:
			endtime = temp.get('content') # balikan posisi akhir timeline ke posisi awal file

		else:
			endtime = "4s" # jika tidak ada data maka buat manual. timeline akhir timeline di 200f/ 4 detik x fps/25
			add_metamenu('end-time',endtime)

		varglo.root_file.set('begin-time',"0f")# awal timeline pastinya di 0f
		varglo.root_file.set('end-time',endtime)

def key_time_add(time):
	
	el_keyframe_this = varglo.root_file.find(".//keyframe[@time='{no}']".format(no= time))
	
	if el_keyframe_this == None:
		metaadd = ET.Element('keyframe')
		metaadd.attrib['time']=time
		metaadd.attrib['active']='true'
		varglo.root_file.insert(1,metaadd)
	else:
		el_keyframe_this.set('active','true')

	el_keyframe_this = varglo.root_file.find(".//keyframe[@time='-2s']") # buat batas input key
	if el_keyframe_this == None:
		metaadd = ET.Element('keyframe')
		metaadd.attrib['time']='-2s'
		metaadd.attrib['active']='false'
		varglo.root_file.insert(1,metaadd)
	else:
		el_keyframe_this.set('active','false')

def set_mode():

	def convert_totime(datatime):
		
		pos = datatime.find("f")
		dt1=datatime[:pos]
		dt2 = float(dt1)/float(varglo.fps)
		pos = str(dt2).find('.')
		datasecon = str(dt2)[:pos]
		pecahan = float(dt1)-float(datasecon)*varglo.fps
		nilaihasil =""

		if float(str(dt2)[pos+1:]) == 0:
			nilaihasil = datasecon+'s'

		else:
			nilaihasil = datasecon+"s "+str(pecahan)+'f'
		
		return nilaihasil

	turnoff_keyframes()	

	if varglo.mode_smartkey == 'inputkey':

		set_range_beginandendtime('inputkey')
		key_time_add(convert_totime(varglo.root_file.get('begin-time')))
		return 'inputkey'

	if varglo.mode_smartkey == 'play':
		set_range_beginandendtime('None')
		turn_on_basic_keyframes('0f')
		return 'play'

	if varglo.mode_smartkey == 'editmode':
		set_range_beginandendtime('edit')
		turn_on_keyframes_editmode()
		#key_time_add(convert_totime(varglo.root_file.get('begin-time')))
		return 'editmode'

def simpan_fileundo(path_undo,root_undo):

	if not varglo.undo:
		if varglo.mode_smartkey == 'play':
			copy_file = copy.deepcopy(varglo.root_file)
			meta_mode = copy_file.find(".//*[@name='shapekey_mode']")
			meta_mode.set('content','inputkey')
			#tree_copy = ET.ElementTree(copy_file)
			#tree_copy.write(path_undo)
			try:
				tree_copy = ET.ElementTree(copy_file)
				tree_copy.write(path_undo)
			except PermissionError:
				print("   >>> File read-only / please install Wayang download version!")
			except OSError as e:
				if e.errno == errno.EACCES:
					print("    >>> permission denied / read-only !")
				else:
					print(f"   >>> Error no: {e}")

			

def convert_to_maprange():

	for el_timeloop in varglo.root_file.findall(".//average/entry/timeloop"):#awal
		el_link_range = el_timeloop.find('.//link_time/fromreal/link/scale/link')
		el_link_inf = el_link_range.find('.//subtract/lhs/')
		guid_inf = el_link_inf.get('guid')

		el_maprange_template = load_template(".//*[@kunci='SK2_to_maprange']")
		el_inf_t = el_maprange_template.find(".//*[@guid='LINK_influence']")
		el_inf_t.set('guid',guid_inf)

		el_controller_t = el_maprange_template.find(".//*[@guid='LINK_TO_BONE']")

		el_controller_f = el_link_range.find('.//range//subtract/lhs/')
		guid_controller = el_controller_f.get('guid')
		value_controller  = el_controller_f.get('value')

		if value_controller == None:
			el_controller_t = el_maprange_template.find(".//*[@guid='LINK_TO_BONE']/..")
			replace(el_controller_t,el_controller_f)

		else:
			el_controller_t.set('guid',guid_controller)
			el_controller_t.set('value',value_controller)

		el_sudmin_f = el_link_range.find('.//range//subtract/rhs/')
		value_sudmin = el_sudmin_f.get('value')

		for el_sudmin_t in el_maprange_template.findall(".//*[@value='sud_min']"):
			el_sudmin_t.set('value',value_sudmin)

		el_sudmax_t = el_maprange_template.find(".//*[@value='sud_max']")
		el_sudmax_f = el_link_range.find('.//range//reciprocal/link/subtract/lhs/')
		value_sudmax = el_sudmax_f.get('value')
		el_sudmax_t.set('value',value_sudmax)

		replace(el_link_range,el_maprange_template[0])

def convert_to_range():

	for el_timeloop in varglo.root_file.findall(".//average/entry/timeloop"):#awal
		el_maprange = el_timeloop.find('.//map_range/..')

		el_link_inf = el_maprange.find('.//link/')
		guid_inf = el_link_inf.get('guid')

		el_range_template = load_template(".//*[@kunci='SK2_range_convert']")
		el_inf = el_range_template.find(".//*[@guid='LINK_influence']")
		el_inf.set('guid',guid_inf)

		el_link_controller = el_maprange.find('.//to_max/map_range/link/')
		guid_controller = el_link_controller.get('guid')
		value_controller = el_link_controller.get('value')

		el_controller_t = el_range_template.find(".//*[@guid='LINK_TO_BONE']")

		if value_controller == None: # mode edit
			el_controller_t = el_range_template.find(".//*[@guid='LINK_TO_BONE']/..")
			replace(el_controller_t,el_link_controller)

		else:
			el_controller_t.set('guid',guid_controller)
			el_controller_t.set('value',value_controller)

		el_link_sudmin = el_maprange.find('.//to_max/map_range/from_min/')
		value_sudmin = el_link_sudmin.get('value')
		el_link_sudmax = el_maprange.find('.//to_max/map_range/from_max/')
		value_sudmax = el_link_sudmax.get('value')

		el_sudmax_t =  el_range_template.find(".//*[@value='sud_max']")
		el_sudmax_t.set('value',value_sudmax)

		for el_sudmin_t in el_range_template.findall(".//*[@value='sud_min']"):
			el_sudmin_t.set('value',value_sudmin)

		replace(el_maprange,el_range_template[0])

def find_parent_layerbone(layer_bone):

	guid_this = layer_bone.get('guid')

	for skeleton in varglo.root_file.findall(".//*[@type='skeleton']"):
		for bone in skeleton.findall(".//bone"):
			guid_bone = bone.get('guid')

			if guid_bone == guid_this:
				el_up = get_parent(skeleton,1)
				return el_up,skeleton
	return None,None

def hide_hook(hide):

	if len(varglo.data_error) >0:
		return

	if not varglo.hook:
		return

	print("    >>> hide Hook done")

	bones = varglo.root_file.find(".//bones")

	if bones == None:
		return

	for layer_hooks in varglo.root_file.findall(".//*[@group='hookcont']"):
		if hide:
			layer_hooks.set('active','false')
		else:
			layer_hooks.set('active','true')

def get_listhook():

	list_starhook = []
	layer_hooks = varglo.root_file.findall(".//*[@group='hookcont']")

	if len(layer_hooks) == 0:
		return list_starhook 

	else:
		for hook in layer_hooks:
			parent_this = get_parent(hook,1)
			hook.set('hook','temp') # kode  nanti di delete jika tidak di pake
			data = [hook,parent_this]
			list_starhook.append(data)
		
		return list_starhook

def set_name_hook(layer_skeleton,el_name,el_hook):

	#CREATE NAME LAYERS
	posr_ = 0
	id_cont = 0
	name_desc = layer_skeleton.get("desc")

	if name_desc != None:
		posr_ = name_desc.find("r_")
		id_cont = name_desc[posr_+2:]

	kata = el_name[0].text
	pos = kata.find("@")
	new_name = "hook_c"+str(id_cont)+"_"+str(varglo.hook_idx)+kata[pos:]
	el_hook.set('desc',new_name)
	varglo.hook_idx +=1

def cek_hook_inpolygon(list_star,guid_hook_bone,parent_this):

	hooked = False

	for hook in list_star:
	 	el_origin = hook[0].find(".//*[@name='origin']/vector")
	 	if 'guid' in el_origin.attrib:
	 		guid_hook = el_origin.get('guid')
	 		if guid_hook_bone == guid_hook:
	 			hooked = True

	 			if parent_this == hook[1]:
	 				hook[0].attrib.pop('hook')

	 			else:# moving to new parent
	 				new_hook = copy.deepcopy(hook[0])
	 				parent_this.append(new_hook)

	 			return True
	return False

def erase_listhook(list_star):

	for hook in list_star:
		if 'hook' in hook[0].attrib:
			hook[1].remove(hook[0])

def make_hook(list_star,guid_bone,parent_this,el_tohook,layer_skeleton,el_name):

	new_el_hook = None
	for hook in list_star:
		el_bonelink = hook[0].find(".//link_on/vectorx//bone_valuenode")
		if el_bonelink != None:
			guid_hook_inpoligon = el_bonelink.get('guid')
			if guid_bone == guid_hook_inpoligon:
				new_el_hook = copy.deepcopy(hook[0])
				break

	if new_el_hook == None:
		guid_hook_bone = el_tohook[0].get('guid')
		if guid_hook_bone == None:
			guid_hook_bone = str(uuid.uuid4())
			el_tohook[0].set('guid',guid_hook_bone)

		el_hook = load_template(".//*[@kunci='SK_hook_polygon']/")
		set_name_hook(layer_skeleton,el_name,el_hook)
		el_origin = el_hook.find(".//*[@guid='GUID_hook']/..")
		el_tohook[0].set('guid',guid_hook_bone)
		replace(el_origin,el_tohook[0])

		el_bonelink = el_hook.find(".//*[@guid='GUID_BONE_IK']")
		el_bonelink.set('guid',guid_bone)
		parent_this.append(el_hook)

	else:
		el_originhook = new_el_hook.find(".//*[@name='origin']")
		replace(el_originhook,el_tohook[0])
		parent_this.append(new_el_hook)

def create_hook():

	if len(varglo.data_error) >0:
		return

	print("[.] create hook")

	list_star = get_listhook()
	list_group_hook = []
	hook_idx= 0
	el_bones = varglo.root_file.find('.//bones')

	for layer_bone in el_bones.findall(".//bone"):
		el_name = layer_bone.find('.//name')

		if el_name != None:
			if el_name[0].tag == 'join':
				el_name = layer_bone.find('.//name/join/after')

			if '_ik' in el_name[0].text:
				parent_this,layer_skeleton = find_parent_layerbone(layer_bone)
				guid_bone = layer_bone.get('guid')
				el_original = layer_bone.find(".//origin/add/..")
				el_tohook = el_original.find(".//add/rhs")
				isi_el_tohook = el_tohook[0][0].text

				if isi_el_tohook == '0.0000000000':
					guid_id = str(uuid.uuid4())
					el_hook = load_template(".//*[@kunci='SK_hook_polygon']/")
					set_name_hook(layer_skeleton,el_name,el_hook)
					el_origin = el_hook.find(".//*[@guid='GUID_hook']/..")

					el_bonelink = el_hook.find(".//link_on/vectorx//bone_valuenode")
					el_bonelink.set('guid',guid_bone)

					el_vec = el_original.find(".//add/lhs")
					guid_original = el_original[0].get('guid')
					el_new_origin = copy.deepcopy(el_vec[0])
					el_new_origin.set('guid',guid_id)
					
					el_tohook = el_original.find(".//add/rhs")
					el_rhs_awal = copy.deepcopy(el_tohook[0])
					isi_rhs = el_rhs_awal[0].text

					el_rhs_awal[0].text = '0.1'
					el_rhs_awal[1].text = '0.1'

					replace(el_vec,el_rhs_awal)
					replace(el_tohook,el_new_origin)
					replace(el_origin,el_new_origin)
					parent_this.append(el_hook)

					for el_ori in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no= guid_original)):
						replace(el_ori,el_original[0])

				else: #ada hook lama, atau link to bone
					if 'guid' in el_tohook[0].attrib: #cek ada hook?
						guid_hook_bone = el_tohook[0].get('guid')

						if not cek_hook_inpolygon(list_star,guid_hook_bone,parent_this): # apakah memiliki hook poligon
							make_hook(list_star,guid_bone,parent_this,el_tohook,layer_skeleton,el_name)

					else:
						make_hook(list_star,guid_bone,parent_this,el_tohook,layer_skeleton,el_name)
						
	erase_listhook(list_star)
	print("[..] done")

def update_skname():

	if len (varglo.shapekey_rename_list) == 0:
		return

	else:
		bones = varglo.root_file.find(".//bones")
		el_controller_bones = bones.findall('.//scalex/switch//link_on/average/entry')
		data_namebone = []

		for layer_bone in el_controller_bones:
			guid_this = layer_bone[0].get('guid')
			layer_bone_this = get_parent(layer_bone,5)

			el_entry = layer_bone_this.findall('.//name/join//dynamic_list/entry')

			for entry in el_entry:
				el_name = entry.find(".//link_off/string")
				el_inf = entry.find(".//link_on/realstring/real/")
				
				if guid_this == el_inf.get('guid'):
					data_namebone.append([guid_this,el_name])

		data_nametext = []
		list_name_SK = varglo.root_file.findall(".//*[@group='name_SK']")
		for layer_text in list_name_SK:
			el_inf = layer_text.find('.//param/switch//link_on/average/entry')
			if not el_inf == None:
				guid_this = el_inf[0].get("guid")
				el_name_text = layer_text.find(".//param/string")
				data_nametext.append([guid_this,el_name_text])

		for dat in varglo.shapekey_rename_list:

			if dat[1] == varglo.nama_controller:
				varglo.nama_controller = dat[2]
				varglo.id_controller = dat[0]

			if not dat[1] == dat[2]:
				for bone in data_namebone: # in bone
					if dat[0] == bone[0]:
						el_name_text = bone[1].text
						bone[1].text = dat[2]

				for text in data_nametext:
					if dat[0] == text[0]:
						text[1].text = dat[2]

def replace_data():

	if len(varglo.data_error) >0:
		return

	if varglo.mode_smartkey == 'play':	
		if len(varglo.valueattime_list) == 0: #if not keys founded
			print('  !!! not found keys, please create keys !!!')
			varglo.root_file = varglo.file_undo 
			return
	
	defs = False
	for do in varglo.controller_data:
		if do[2]=="append":
			do[0].append(do[1])

		if do[2]=="masukan":
			do[0].insert(0,do[1])

		if do[2]=="masukan1":
			do[0].insert(1,do[1])

		if do[2]=="replace":
			replace(do[0],do[1])

		if do[2]=="set":
			pos = do[1].find(">")
			end_name = '@shapekey'
			if do[0].tag == 'layer':

				if do[0].get('type') in ['group','switch']:
					end_name = '@key'
			do[0].set('desc',do[1][:pos]+end_name)

		if do[2]=="clear":
			desc_text = do[0].get('desc')
			pos = desc_text.find(">")
			do[0].set('desc',desc_text[:pos+1])

		if do[2]=="pop":
			if 'group' in do[0].attrib:
				do[0].attrib.pop('group')

		if do[2]=="remove":
			do[0].remove(do[1])

		if do[2]=="add":

			text = do[0].get('desc')
			if text != None:
				if not "@" in text:
					do[0].set('desc',str(text)+"@shapekey")
			else:
				do[0].set('desc',"Rotate@shapetkey")

		if do[2]=="use":
			do[0].set('use',do[1])

		if do[2]=="replaceall":
			for el_base in varglo.root_file.findall(".//*/[@guid='{no}']/..".format(no= do[0])):
				replace(el_base,do[1])
				##varglo.controller_data.append([guid_base,el_base,"replaceall"])
		if do[2]=="ganti":
			desc_text = do[0].get('desc')
			pos = desc_text.find(">")
			new_text = desc_text[:pos+1]+varglo.updateok_com
			do[0].set('desc',new_text)

		if do[2]=="ganti_kode":
			text = do[0].text
			pos = text.find(">")
			new_text = do[1]
			do[0].text = new_text

	convert_keys_tolinear(varglo.root_file)
	erase_shapekey() #modul erase when edit but not edit but user erase keys
	
def convert_export_toguidlink():

	def find_exported(name_id,el_ini): # find it and append that elements
		
		for el_this in varglo.root_file.iter():
			for attr, value in list(el_this.attrib.items()):
				if value == name_id:
					a = ET.Element(attr)
					a.append(el_ini)
					el_this.attrib.pop(attr)
					el_this.append(a)

	layer_defs = get_defs()
	
	for el_export in layer_defs.findall(".//*[@id]"): # find in export valuenode
		name_id = el_export.get('id')
		if 'shapekey' in name_id:
			continue
		el_ini = copy.deepcopy(el_export)
		el_ini.attrib.pop('id')
		layer_defs.remove(el_export)
		guid_this =str(uuid.uuid4())
		el_ini.set('guid',guid_this)
		find_exported(name_id,el_ini)
		
def mulai_process():

	if varglo.mode_smartkey == 'editmode':  #dari play ke mode edit
		hide_hook(True)
		#print("1645 :",'Enter Edit MODE')
		find_controller_and_editkey()

	else: #to mode play
		if varglo.mode_before == 'inputkey': # dari input key to play
			#print("1621 :from inputkey to play MODE ")
			varglo.controller_data = []
			buat_controller() #convert bone to be controller bone
			create_list_shapekeys() #create name of controller text

		if varglo.mode_before == 'editmode': #dari mode edit ke play
			#print("1631 :frrom editmode to Play MODE")
			set_get_controller_active()
			
		find_animasi_dan_convert(varglo.mode_before )#baru
		erase_export_shapekeys()
		hide_hook(False)
	append_timeloop()
	replace_data()

def wayang(file, namafile):
	#LOAD TEMPLETE
	template_filename = os.path.join(os.path.dirname(sys.argv[0]), 'convert_template.xml')
	if template_filename !=None:
		tree_convert = ET.parse(template_filename)
		varglo.main_template = tree_convert.getroot()
		varglo.root_file = file
		varglo.raw_file = copy.deepcopy(file)
	else:
		varglo.data_error['template']= 'missing'

	#LOAD undo file
	path_undo = os.path.join(os.path.dirname(sys.argv[0]),'undo.sif')
	tree_undo = ET.parse(path_undo)
	root_undo = tree_undo.getroot()

	varglo.file_undo = copy.deepcopy(root_undo)
	varglo.id = str(uuid.uuid4()) #id_sudut
	#varglo.fps = float(varglo.root_file.get('fps')) # get fps # sebaiknya fps 25
	varglo.root_file.set('fps','25') #set defaul to 25 fps
	varglo.fps = 25 # default fps don't change

	convert_export_toguidlink() # will convert export value node to normal but still conected because have guid id
	get_set_mode() # menu GTK and setting
	update_skname()
	simpan_fileundo(path_undo,root_undo)

	if not varglo.synfig_above_154:# old synfig , convert element range to map range
		convert_to_maprange() # becouse old synfig not have map_range converter so we use range converter manualy calculation
		#to_min + (seek - from_min) * (to_max - to_min) / (from_max - from_min) formula map_range

	if varglo.mode_smartkey != 'None':
		if varglo.mode_smartkey in ['editmode','inputkey'] or varglo.mode_before == 'inputkey':
			find_infcontroller()

		if set_mode() in varglo.mode: # mode edit atau play/ dari input key ke play/second after [A]
			print("880 varglo.mode :",varglo.mode)
			mulai_process()
			
		else: #masuk mode input
			hide_hook(True)
			change_timeloop_to_basevalue() #change shapekey to defs data temporary
			append_timeloop()
			replace_data()
	
	if len(varglo.data_error) ==0:
		if not varglo.synfig_above_154:# old synfig
			convert_to_range()

	else:
		varglo.root_file = varglo.file_undo # load undo file

	if varglo.mode_smartkey == 'play':
		if varglo.hook:
			if varglo.mode_before == 'inputkey':
				create_hook()
		set_infcontroller()

	#CEK file SYNFIG RESULT FOR DEVELOPER
	print(" ")
	print(bcolors.UNDERLINE + "|||||     Wayang plugin.....Done!     |||||" + bcolors.ENDC)
		
	#if varglo.developer:
		#print(' ')
		#print("create output for cek in edit script")
		#ET.indent(varglo.root_file)
		#tree_copy = ET.ElementTree(varglo.root_file)
		#tree_copy.write('/home/mint/Documents/'+'cek_output2025.sif')

def update_file():

	from GTKtools import show_message

	if len(varglo.data_error)!= 0:
		varglo.root_file = varglo.raw_file
		print("   ! make controller failed !")
		show_message("make controller failed !","ERROR")

	else:
		match varglo.mode_smartkey:
			case 'play':
				show_message("controller plugin success","INFO")
			case 'editmode':
				show_message("plugin edit MODE","INFO")
			case 'inputkey':
				show_message("plugin inputkeys MODE","INFO")
			case None:
				show_message("plugin Tools MODE","INFO")

	if((len(sys.argv) > 2 )):
			hasil = sys.argv[2]
	else:
		if varglo.developer:
			hasil = os.path.join(os.path.dirname(sys.argv[0]), varglo.namafile)
			varglo.root_file=varglo.raw_file

		else:
			hasil = sys.argv[1]

	el_tree = ET.ElementTree(varglo.root_file)
	with open(hasil, "wb") as filesnew:
		el_tree.write(filesnew)

def inti():
	print(" ")
	print(bcolors.UNDERLINE + "|||||     Wayang plugin.....processing!     |||||" + bcolors.ENDC)
	onsynfig = len(sys.argv)
	if onsynfig == 1:
		varglo.developer = True
		template_filename = os.path.join(os.path.dirname(sys.argv[0]), varglo.namafile)
		tree_convert = ET.parse(template_filename)
		akar_file = tree_convert.getroot()
		wayang(akar_file,varglo.namafile)
		update_file()

	else:
		varglo.developer = False
		varglo.namafile =""
		if len(sys.argv) < 2:
			pass
		else:
			varglo.namafile = os.path.basename(sys.argv[1])
		akar_file = ET.parse(sys.argv[1]).getroot()
		wayang(akar_file,varglo.namafile)
		update_file()
		
if __name__ == "__main__":
	inti()
