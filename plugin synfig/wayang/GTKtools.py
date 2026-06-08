# Synfig plugin: Shapekey 1.0
# Helps controller shape/animated node
# (c) 2025 2026 ZAINAL IDN

import varglo
import math

try:
	import gi
	gi.require_version("Gtk", "3.0")
	from gi.repository import Gtk,Gdk

except ModuleNotFoundError:
	print("    !!! GTK modul not found. please install GTK!!!                   ")
	varglo.modul_GTK = False

if varglo.modul_GTK:
	settings = Gtk.Settings.get_default()
	settings.set_property("gtk-application-prefer-dark-theme", True)


def cari_file():

	class MainWindow(Gtk.Window):
		Gtk.filepath = None

		def __init__(self):
			Gtk.Window.__init__(self, title="Pilih File")

			self.set_default_size(300, 50)
			button = Gtk.Button(label="Cari ... ")
			button.connect("clicked", self.on_open_file)
			self.add(button)

		def on_open_file(self, widget):

			dialog = Gtk.FileChooserDialog(
			title="Pilih File",
			parent=self,
			action=Gtk.FileChooserAction.OPEN
			)

			dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK
			)

			response = dialog.run()

			if response == Gtk.ResponseType.OK:
				Gtk.filepath = dialog.get_filename()
				Gtk.main_quit()

			dialog.destroy()


	win = MainWindow()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()
	Gtk.main()

	return Gtk.filepath

def select_bone(list_bones):

	class RadioListBoxWindow(Gtk.Window):

		Gtk.pilih = 'none'
		def __init__(self):
			Gtk.Window.__init__(self, title="Select bone controller")
			self.set_border_width(10)
			self.set_default_size(300, 100)

			main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
			self.add(main_vbox)

			# List untuk menyimpan RadioButto
			page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			page1.set_border_width(10)
			page1.pack_start(Gtk.Label(label="Bones"), False, False, 0)

			self.radio_buttons = []

			scrolled_window = Gtk.ScrolledWindow()
			scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window.set_min_content_height(200)
			# Buat ListBox
			self.listbox = Gtk.ListBox()
			self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
			#
			scrolled_window.add(self.listbox)
			page1.pack_start(scrolled_window, False, False, 0)
			main_vbox.pack_start(page1, False, False, 0)

			# Daftar pilihan radio
			radio_group = None
			idx=0

			for choice, id_bone,obj in list_bones:
				row = Gtk.ListBoxRow()
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
				row.add(hbox)

				# Buat RadioButton
				if radio_group is None:
					radio_button = Gtk.RadioButton.new_with_label_from_widget(None, choice)
					radio_group = radio_button
				else:
					radio_button = Gtk.RadioButton.new_with_label_from_widget(radio_group, choice)

				# Tambahkan signal saat diklik
				radio_button.connect("toggled", self.on_radio_toggled)
				radio_button.idx = obj
				# Simpan ke list
				self.radio_buttons.append(radio_button)

				hbox.pack_start(radio_button, True, True, 0)
				self.listbox.add(row)

				idx +=1

			# Tombol yang label-nya akan berubah
			self.button = Gtk.Button(label="select Bone")
			self.button.info = list_bones[0][2]
			self.listbox.add(Gtk.ListBoxRow())
			self.button.connect("clicked", self.on_button_plih)
			main_vbox.pack_start(self.button , False, False, 0)

			self.show_all()

		def on_button_plih(self, button):

			Gtk.pilih = button.info
			Gtk.main_quit()

		def on_radio_toggled(self, radio_button):
			if radio_button.get_active():
				label = radio_button.get_label()
				self.button.set_label(f"OK")
				self.button.info = radio_button.idx

	win = RadioListBoxWindow()
	win.connect("destroy", Gtk.main_quit)
	Gtk.main()

	return Gtk.pilih

def show_message(message,tipe = None, parent=None):

	if varglo.modul_GTK:
		tipenya = None
		if tipe == 'INFO':
			tipenya = Gtk.MessageType.INFO
		if tipe == 'ERROR':
			tipenya = Gtk.MessageType.ERROR
		if tipe == 'WARNING':
			tipenya = Gtk.MessageType.WARNING

		dialog = Gtk.MessageDialog(
			parent=parent,
			message_type=tipenya,
			buttons=Gtk.ButtonsType.OK,
			text=message
		)
		dialog.run()
		dialog.destroy()

def show_warning(pesan ,parent=None):

	Gtk.respon = 'none'

	dialog = Gtk.MessageDialog(
		parent=parent,
		flags=0,
		message_type=Gtk.MessageType.QUESTION,
		buttons=Gtk.ButtonsType.OK_CANCEL,
		text= "WARNING!"
		)

	dialog.format_secondary_text("Are you sure delete shapekey "+pesan+" ?")

	response = dialog.run()

	if response == Gtk.ResponseType.OK:
		Gtk.respon = 'OK'

	elif response == Gtk.ResponseType.CANCEL:
		Gtk.respon = 'cancel'

	dialog.destroy()

	return Gtk.respon

def show_shapekey_dialog(awal):



	Gtk.awal = awal
	Gtk.tab2 = None
	Gtk.apa = 'smartkey'
	Gtk.jenis = 'smartkey'
	if len(varglo.smartkey_list)!=0:
		Gtk.jenis = varglo.smartkey_list[0][1]

	Gtk.wtemplate = True
	Gtk.IKtemplate = True
	Gtk.SKtemplate = True
	Gtk.ikjenis = 'ik1'
	Gtk.undo = 'undo_1'
	Gtk.clone = None

	class isi_clone(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

			self.undo = ''
			self.set_border_width(10)

			scrolled_window2 = Gtk.ScrolledWindow()
			scrolled_window2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window2.set_min_content_height(260)
			
			listbox2 = Gtk.ListBox()
			listbox2.set_selection_mode(Gtk.SelectionMode.SINGLE)
			scrolled_window2.add(listbox2)

			self.daftar_list2 = listbox2
			nama_label = "Clone Shapekey"
			#varglo.clone_layergroup = 'none'
			if not varglo.clone_layergroup == 'none':
				row_temp2 = None
				#for i in varglo.undo_list:
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
				check = Gtk.CheckButton(label=varglo.clone_layergroup)
				check.connect("toggled", self.on_skeleton_toggled, varglo.clone_layergroup)

				row = Gtk.ListBoxRow()
				row.add(hbox)
				listbox2.add(row)
				hbox.pack_start(check, False, False, 0)

			else:
				nama_label = "Not found yourgroup>clone!!"
	        
			button_box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			ok_button3 = Gtk.Button(label="OK")
			ok_button3.connect("clicked", self.on_ok_clone_clicked)
			cancel_button3 = Gtk.Button(label="Cancel")

			self.pack_start(Gtk.Label(label=nama_label), False, False, 0)
			self.pack_start(scrolled_window2, True, False, 0)

		def on_ok_clone_clicked(self, button):

			Gtk.jenis = self.clone
			Gtk.apa ='clone'
			
			Gtk.main_quit()

		def on_skeleton_toggled(self, checkbutton, index):

			self.clone = index
			Gtk.clone = index

	class isi_undo(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

			self.undo = ''
			self.set_border_width(10)

			scrolled_window2 = Gtk.ScrolledWindow()
			scrolled_window2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window2.set_min_content_height(260)
			
			listbox2 = Gtk.ListBox()
			listbox2.set_selection_mode(Gtk.SelectionMode.SINGLE)
			scrolled_window2.add(listbox2)

			self.daftar_list2 = listbox2
			varglo.undo_list.sort()

			row_temp2 = None
			for i in varglo.undo_list:
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
				check = Gtk.CheckButton(label=i)
				check.connect("toggled", self.on_skeleton_toggled, i)

				row = Gtk.ListBoxRow()
				row.add(hbox)
				listbox2.add(row)
				hbox.pack_start(check, False, False, 0)
				if i ==1:
					row_temp2 = row
	        
			listbox2.select_row(row_temp2) # slect pertmana
			button_box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			ok_button3 = Gtk.Button(label="OK")
			ok_button3.connect("clicked", self.on_ok_undo_clicked)
			cancel_button3 = Gtk.Button(label="Cancel")

			self.pack_start(Gtk.Label(label="Undo Shapekey"), False, False, 0)
			self.pack_start(scrolled_window2, True, False, 0)

		def on_ok_undo_clicked(self, button):

			Gtk.jenis = self.undo
			Gtk.apa ='undo'
			Gtk.main_quit()

		def on_skeleton_toggled(self, checkbutton, index):

			self.undo = index
			Gtk.undo = index

	class ShapekeysNotebook(Gtk.Notebook):
		def __init__(self):
			super().__init__()
			self.connect("switch-page", self.on_tab_switched)
			self.set_tab_pos(Gtk.PositionType.TOP)

			self.isiSmartkey = isieditsk()
			self.append_page(self.isiSmartkey, Gtk.Label(label="Edit or Bind"))

			self.isiik = frezesk()
			self.append_page(self.isiik, Gtk.Label(label="frezze"))

		def on_tab_switched(self, notebook, current_page, page_num):
			if page_num == 0:
				Gtk.apa = 'edit'
			else:
				Gtk.apa = 'frezze'

	class frezesk(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			
			self.set_border_width(10)
			self.pack_start(Gtk.Label(label="Shapekeys"), False, False, 0)
		
			scrolled_window = Gtk.ScrolledWindow()
			scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window.set_min_content_height(300)
			
			listbox = Gtk.ListBox()
			listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
			scrolled_window.add(listbox)

			self.daftar_list = listbox
			row_temp = None
			self.sk = []
			self.dataklik=[None,None]

			for i in varglo.smartkey_list:
				label = Gtk.Label(label=i[1], xalign=0)
				self.row = Gtk.ListBoxRow()
				hbox1 = Gtk.HBox(spacing=6)
				self.row.add(label)
				self.row.id = i[0]
				self.row.text = i[1]
				listbox.add(self.row)# awal
				self.sk.append([i[0],i[1],i[1]]) # 0=guid,1=orinal name,2=new name
				if i ==1:
					row_temp = row

			varglo.shapekey_rename_list = []
			self.button_boxp1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			listbox.select_row(row_temp) # slect pertmana
			listbox.connect("row-activated", self.on_activate)

			sk_first = varglo.smartkey_list[0][1]
			self.pack_start(scrolled_window, False, False, 0)
			
		def on_activate(self, listbox, row):
			
			if row:
				label = row.get_child()
				text_sk = label.get_text()
				Gtk.jenis = row.text
				
	class isieditsk(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			
			self.set_border_width(10)
			self.pack_start(Gtk.Label(label="Edit Shapekeys"), False, False, 0)
		
			scrolled_window = Gtk.ScrolledWindow()
			scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window.set_min_content_height(300)
			
			listbox = Gtk.ListBox()
			listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
			scrolled_window.add(listbox)

			self.daftar_list = listbox

			row_temp = None

			self.sk = []
			self.dataklik=[None,None]

			for i in varglo.smartkey_list:
				label = Gtk.Label(label=i[1], xalign=0)
				self.row = Gtk.ListBoxRow()
				hbox1 = Gtk.HBox(spacing=6)
				self.row.add(label)
				self.row.id = i[0]
				self.row.text = i[1]
				listbox.add(self.row)# awal

				self.sk.append([i[0],i[1],i[1]]) # 0=guid,1=orinal name,2=new name
				if i ==1:
					row_temp = row

			varglo.shapekey_rename_list = []
			self.button_boxp1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			listbox.select_row(row_temp) # slect pertmana
			listbox.connect("row-activated", self.on_activate)

			sk_first = varglo.smartkey_list[0][1]
			self.entry_min = Gtk.Entry()
			self.entry_min.set_text(sk_first)
			self.entry_min.connect("focus-out-event", self.on_selesai)
			
			ok_button = Gtk.Button(label="Delete Shapekey")
			ok_button.connect("clicked", self.on_del_clicked)

			self.pack_start(scrolled_window, False, False, 0)
			
			self.pack_start(self.entry_min, True, False, 0)
			self.pack_start(ok_button, True, False, 0)

		def on_del_clicked(self, button):
			
			apa = show_warning(self.dataklik[1])
			if apa =='OK':
				Gtk.jenis = self.dataklik[1]
				self.dataklik[0].set_text("deleted")

				idx = 0
				for data in self.sk:
					if data[1]==self.dataklik[1]:
						self.sk[idx][2]="deleted"
					idx +=1
				varglo.shapekey_rename_list = self.sk

			else:
				print("    >>> cancel delete shapekey")

		def on_selesai(self, entry,event):

			textnya = entry.get_text()
			self.dataklik[0].set_text(textnya)
			
			idx = 0
			for data in self.sk:
				if data[1]==self.dataklik[1]:
					self.sk[idx][2]=textnya
				idx +=1
			varglo.shapekey_rename_list = self.sk

		def on_entry_changed(self, entry):
			try:
				textnya = entry.get_text()
						
			except ValueError:
				pass

		def on_activate(self, listbox, row):
			
			if row:
				label = row.get_child()
				text_sk = label.get_text()
				self.entry_min.set_text(text_sk)
				self.dataklik[0] =label
				self.dataklik[1] =text_sk
				Gtk.jenis = row.text

	class dataisiik(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

			button_box_ikjenis2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
			self.set_border_width(10)
			self.listcheckbutton = []

			boxgambar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
			boxgambar.set_size_request(200, 121)
			self.image = Gtk.Image.new_from_file("icon1.png")
			boxgambar.pack_start(self.image, True, True, 0)
			
			ik_jenis1 = Gtk.CheckButton.new_with_label("IK 2 joint human manual")
			ik_jenis1.connect("toggled", self.on_jenisIK_toggled,'ik1')
			ik_jenis1.set_active(True)
			button_box_ikjenis2.pack_start(ik_jenis1, False, True, 0)
			
			ik_jenis2 = Gtk.CheckButton.new_with_label("IK 3 joint Escavator manual")
			ik_jenis2.connect("toggled", self.on_jenisIK_toggled,'ik2')
			ik_jenis2.set_active(False)
			button_box_ikjenis2.pack_start(ik_jenis2, False, True, 0)

			ik_jenis2b = Gtk.CheckButton.new_with_label("IK 3 joint Animal manual")
			ik_jenis2b.connect("toggled", self.on_jenisIK_toggled,'ik2b')
			ik_jenis2b.set_active(False)
			button_box_ikjenis2.pack_start(ik_jenis2b, False, True, 0)

			ik_jenis3 = Gtk.CheckButton.new_with_label("IK 2 joint human converter")
			ik_jenis3.connect("toggled", self.on_jenisIK_toggled,'ik3')
			ik_jenis3.set_active(False)
			button_box_ikjenis2.pack_start(ik_jenis3, False, True, 0)

			ik_jenis4 = Gtk.CheckButton.new_with_label("IK 3 joint Escavator converter")
			ik_jenis4.connect("toggled", self.on_jenisIK_toggled,'ik4')
			ik_jenis4.set_active(False)
			button_box_ikjenis2.pack_start(ik_jenis4, False, True, 0)

			ik_jenis4b = Gtk.CheckButton.new_with_label("IK 3 joint Animal converter")
			ik_jenis4b.connect("toggled", self.on_jenisIK_toggled,'ik4b')
			ik_jenis4b.set_active(False)
			
			button_box_ikjenis2.pack_start(ik_jenis4b, False, False, 0)

			button_boxp1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			ok_button = Gtk.Button(label="OK")
			ok_button.connect("clicked", self.on_ok_New_clicked)
			cancel_button = Gtk.Button(label="Cancel")

			check_editable = Gtk.CheckButton(label="With Template")
			check_editable.connect("toggled", self.on_template_toggled)
			check_editable.set_active(True)

			button_boxp1.pack_start(check_editable, False, False, 0)
			button_box_ikjenis2.set_hexpand(True)
			
			self.pack_start(button_box_ikjenis2, False, False, 0)
			self.pack_start(boxgambar, False, False, 0)
			self.pack_start(button_boxp1, False, False, 0)

			self.listcheckbutton.append(ik_jenis1)
			self.listcheckbutton.append(ik_jenis2)
			self.listcheckbutton.append(ik_jenis2b)
			self.listcheckbutton.append(ik_jenis3)
			self.listcheckbutton.append(ik_jenis4)
			self.listcheckbutton.append(ik_jenis4b)

			ik_jenis1.set_sensitive(True)
			ik_jenis2.set_sensitive(True)
			ik_jenis2b.set_sensitive(True)
			ik_jenis3.set_sensitive(True)
			ik_jenis4.set_sensitive(True)
			ik_jenis4b.set_sensitive(True)

			ik_jenis1.set_tooltip_text("IK with 2 bone joint human, create by smartkey")
			ik_jenis2.set_tooltip_text("IK with 3 bone joint animal, create by smartkey")
			ik_jenis2b.set_tooltip_text("IK with 3 bone joint spider, create by smartkey")
			ik_jenis3.set_tooltip_text("IK with 2 bone joint human, Only if IK converter evailable in your synfig")
			ik_jenis4.set_tooltip_text("IK with 3 bone joint animal, Only if IK converter evailable in your synfig")
			ik_jenis4b.set_tooltip_text("IK with 3 bone joint animal spider, Only if IK converter evailable in your synfig")

		def on_jenisIK_toggled(self, button,jenis):

			value = button.get_active()
			if value:
				Gtk.jenis = 'ik'
				Gtk.ikjenis = jenis

				if jenis in ['ik1','ik3']:
					self.image.set_from_file("icon1.png")

				if jenis in ['ik2','ik4']:
					self.image.set_from_file("icon2.png")

				if jenis in ['ik2b','ik4b']:
					self.image.set_from_file("icon3.png")
				
				for cb in self.listcheckbutton:
					if cb != button:
						cb.set_active(False) 

		def on_ok_New_clicked(self, button):

			Gtk.apa = 'new smartkey'
			Gtk.jenis = 'ik'
			Gtk.main_quit()	

		def on_template_toggled(self, button):

			value = button.get_active()
			Gtk.IKtemplate = value
			Gtk.wtemplate  = value

	class dataisimerge(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

			self.list_merge = []
			self.set_border_width(10)

			scrolled_window2 = Gtk.ScrolledWindow()
			scrolled_window2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			scrolled_window2.set_min_content_height(260)
			
			listbox2 = Gtk.ListBox()
			listbox2.set_selection_mode(Gtk.SelectionMode.SINGLE)
			scrolled_window2.add(listbox2)

			self.daftar_list2 = listbox2
			
			varglo.skeleton_list.sort()

			row_temp2 = None
			for i in varglo.skeleton_list:
				hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
				check = Gtk.CheckButton(label=i[0]+"  "+i[1], xalign=0)
				check.connect("toggled", self.on_skeleton_toggled, i)

				row = Gtk.ListBoxRow()
				row.add(hbox)
				listbox2.add(row)
				hbox.pack_start(check, False, False, 0)
				if i ==1:
					row_temp2 = row
	        
			listbox2.select_row(row_temp2) # slect pertmana
			button_box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			ok_button3 = Gtk.Button(label="OK")
			ok_button3.connect("clicked", self.on_ok_merge_clicked)
			cancel_button3 = Gtk.Button(label="Cancel")
			#cancel_button3.connect("clicked", self.on_cancel_clicked)

			button_box3.pack_end(ok_button3, False, False, 0)
			button_box3.pack_end(cancel_button3, False, False, 0)

			ket = "Skeleton"
			if len(varglo.skeleton_list)==0:
				ket = 'Not Skeleton layer found !'

			self.pack_start(Gtk.Label(label=ket), False, False, 0)
			self.pack_start(scrolled_window2, True, False, 0)

		def on_ok_merge_clicked(self, button):

			if len(self.list_merge)>1:
				Gtk.jenis = self.list_merge
				Gtk.apa ='merge'
				Gtk.main_quit()

			else:
				print("    !!! skeleton must select 2 layers / no layers skeleton found!!")
				Gtk.apa = None
				Gtk.main_quit()

		def on_skeleton_toggled(self, checkbutton, index):

			if checkbutton.get_active():
				if not index[2] in self.list_merge:
					self.list_merge.append(index[2])
			else:
				if index[2] in self.list_merge:
					self.list_merge.remove(index[2])

			if len(self.list_merge)>0:
				Gtk.jenis = self.list_merge

	class dataisiSmartkey(Gtk.Box):
		def __init__(self):
			super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

			self.min_angle_deg = 135
			self.max_angle_deg = 45
			self.radius = 100
			self.textsudut = "45"
			self.set_border_width(10)
			button_boxp1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			check_editable = Gtk.CheckButton(label="With Template")
			check_editable.connect("toggled", self.on_template_toggled)
			check_editable.set_active(True)
			button_boxp1.pack_start(check_editable, False, False, 0)

			self.button_box_sksudut = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
			self.button_box_sksudut.set_size_request(300, 200)
			self.drawing_area = Gtk.DrawingArea()
			self.drawing_area.set_size_request(200, 180)
			self.drawing_area.connect("draw", self.on_draw)
			self.button_box_sksudut.pack_start(self.drawing_area, False, False, 0)

			# --- Kontrol Sudut Min ---
			hbox1 = Gtk.HBox(spacing=6)
			label_min = Gtk.Label(label="Max (deg):")
			self.slider_min = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -180, 180, 1)
			self.slider_min.set_name("my_custom_scale")
			self.slider_min.set_value(self.min_angle_deg)
			self.slider_min.set_digits(0)
			self.slider_min.set_hexpand(True)
			#self.slider_min.set_draw_value(True)
			self.slider_min.connect("value-changed", self.on_slider_min_changed)
			self.entry_min = Gtk.Entry()
			self.entry_min.set_text(str(self.min_angle_deg))
			self.entry_min.set_width_chars(6)
			self.entry_min.connect("changed", self.on_entry_min_changed)
			hbox1.pack_start(label_min, False, False, 0)
			hbox1.pack_start(self.slider_min, True, True, 0)
			hbox1.pack_start(self.entry_min, False, False, 0)

			hbox2 = Gtk.HBox(spacing=6)
			label_max = Gtk.Label(label="Min (deg):")
			self.slider_max = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -180, 180, 1)
			self.slider_max.set_value(self.max_angle_deg)
			self.slider_max.set_digits(0)
			self.slider_max.connect("value-changed", self.on_slider_max_changed)
			self.entry_max = Gtk.Entry()
			self.entry_max.set_text(str(self.max_angle_deg))
			self.entry_max.set_width_chars(6)
			self.entry_max.connect("changed", self.on_entry_max_changed)
			hbox2.pack_start(label_max, False, False, 0)
			hbox2.pack_start(self.slider_max, True, True, 0)
			hbox2.pack_start(self.entry_max, False, False, 0)
			self.button_box_sksudut.pack_start(hbox1, False, False, 0)
			self.button_box_sksudut.pack_start(hbox2, False, False, 0)
			self.pack_start(Gtk.Label(label="New Shapekey"), False, False, 0)
			self.pack_start(self.button_box_sksudut, False, False, 0)
			self.pack_start(button_boxp1, False, False, 0)

		def on_template_toggled(self, button):

			value = button.get_active()
			Gtk.SKtemplate = value
			Gtk.wtemplate = value

		def on_slider_changed(self, slider):

			self.min_angle_deg = self.slider_min.get_value()
			self.max_angle_deg = self.slider_max.get_value()
			self.drawing_area.queue_draw()
		
		def on_draw(self, widget, cr):

			varglo.sudut_max = self.min_angle_deg
			varglo.sudut_min = self.max_angle_deg

			width = widget.get_allocated_width()
			height = widget.get_allocated_height()
			center_x = width // 2
			center_y = height // 2

			cr.set_source_rgb(1, 1, 1)
			cr.set_font_size(20)
			cr.move_to(center_x-15, center_y-30)

			if self.max_angle_deg >= self.min_angle_deg:
				self.min_angle_deg =self.max_angle_deg
				val = self.min_angle_deg
				self.entry_min.set_text(str(int(val)))
				self.slider_min.set_value(val)

			sud = self.min_angle_deg-self.max_angle_deg

			cr.show_text(str(int(sud))+"°")
			cr.translate(center_x, center_y)  # Geser ke tengah
			cr.scale(1, -1)  # Balik sumbu Y → rotasi CCW

			cr.set_line_width(2)
			# Gambar garis ke sudut minimum (warna merah)
			cr.set_source_rgb(1, 0, 0)
			self.draw_angle_line(cr, math.radians(self.max_angle_deg))
			# Gambar garis ke sudut maksimum (warna hijau)
			cr.set_source_rgb(0, 1, 0)
			self.draw_angle_line(cr, math.radians(self.min_angle_deg))
			# Gambar arc dari min ke max (warna biru transparan)
			cr.set_source_rgba(0, 0, 1, 0.3)
			self.draw_angle_arc(cr,
			    math.radians(self.min_angle_deg),
			    math.radians(self.max_angle_deg)
			)
			# Gambar lingkaran pusat
			cr.set_source_rgb(0, 0, 0)
			cr.arc(0, 0, 4, 0, 2 * math.pi)
			cr.fill()

		def draw_angle_line(self, cr, angle_rad):
			x = self.radius * math.cos(angle_rad)
			y = self.radius * math.sin(angle_rad)
			cr.move_to(0, 0)
			cr.line_to(x, y)
			cr.stroke()

		def draw_angle_arc(self, cr, angle_start, angle_end):
			# Pastikan urutan arc searah jarum jam (positif)
			while angle_end < angle_start:
			    angle_end += 2 * math.pi

			cr.arc(0, 0, self.radius * 0.8, angle_end, angle_start)
			cr.line_to(0, 0)
			cr.close_path()
			cr.fill()	

		def on_slider_max_changed(self, slider):
			val = slider.get_value()
			self.max_angle_deg = val
			self.entry_max.set_text(str(int(val)))
			self.drawing_area.queue_draw()

		def on_entry_max_changed(self, entry):
			try:
				val = float(entry.get_text())
				self.max_angle_deg = val
				self.slider_max.set_value(val)
				self.drawing_area.queue_draw()
			except ValueError:
				pass

		def on_entry_min_changed(self, entry):
			try:
				val = float(entry.get_text())
				self.min_angle_deg = val
				self.slider_min.set_value(val)
				self.drawing_area.queue_draw()
			except ValueError:
				pass

		def on_slider_min_changed(self, slider):

			val = slider.get_value()
			self.min_angle_deg = val
			self.entry_min.set_text(str(int(val)))
			self.drawing_area.queue_draw()

	class InnerNotebook(Gtk.Notebook):
		def __init__(self):
			super().__init__()

			self.connect("switch-page", self.on_tab_switched)
			self.set_tab_pos(Gtk.PositionType.TOP)

			#page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
			#page2.set_border_width(10)

			self.isiSmartkey = dataisiSmartkey()
			self.append_page(self.isiSmartkey, Gtk.Label(label="Bone controller"))

			#self.isislider = dataisislider()
			#self.append_page(self.isislider, Gtk.Label(label="Slider"))

			self.isiik = dataisiik()
			self.append_page(self.isiik, Gtk.Label(label="IK controller"))

		def on_tab_switched(self, notebook, current_page, page_num):

			if len(varglo.smartkey_list)==0:
				if page_num == 1:
					Gtk.jenis = 'ik'

				if page_num == 0:
					Gtk.jenis = 'smartkey'

			else:
				if page_num == 1:
					Gtk.tab2  = 'ik'
					Gtk.wtemplate = Gtk.IKtemplate

				if page_num == 0:
					Gtk.tab2 = 'smartkey'
					Gtk.wtemplate = Gtk.SKtemplate
			
	class MyWindow(Gtk.Window):
		def __init__(self):
			Gtk.Window.__init__(self, title="WAYANG")
			
			self.set_border_width(10)
			self.set_default_size(400, 200)

			main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
			self.add(main_vbox)

			self.notebook = Gtk.Notebook()
			self.notebook.connect("switch-page", self.on_tab_switched)

			main_vbox.pack_start(self.notebook, True, True, 0)
			button_boxp1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

			ok_button = Gtk.Button(label="OK")
			ok_button.connect("clicked", self.on_ok_clicked)

			cancel_button = Gtk.Button(label="Cancel")
			cancel_button.connect("clicked", self.on_cancel_clicked)

			button_boxp1.pack_end(cancel_button, False, False, True)
			button_boxp1.pack_end(ok_button, False, False, 0)
			
			main_vbox.pack_end(button_boxp1, True, True, 0) # tombol ok cancell utama

			if Gtk.awal:
				pass
			else:
				#EDIT BIND OR DELETE SHAPEKEYS
				self.dataisieditsk = ShapekeysNotebook()
				#self.dataisieditsk = isieditsk() # old
				self.notebook.append_page(self.dataisieditsk, Gtk.Label(label="Shapekey"))

			#>> tab for NEW Smartkey <<
			self.inner_notebook_instance = InnerNotebook()
			self.notebook.append_page(self.inner_notebook_instance, Gtk.Label(label="Create"))
			
			##>> MERGE MENU <<
			self.isimerge = dataisimerge()
			self.notebook.append_page(self.isimerge, Gtk.Label(label="Merge Layers"))

			##>> UNDO MENU <<
			self.undo = isi_undo()
			self.notebook.append_page(self.undo, Gtk.Label(label="Undo"))

			##>>CLONE SHAPEKEY<<
			self.clone = isi_clone()
			self.notebook.append_page(self.clone, Gtk.Label(label="Clone shapekey"))

			self.show_all()	

		def on_ok_clicked(self, button):

			#print("    >>> Ok exit dialog gtk ")

			if Gtk.apa == 'new smartkey':
				if not Gtk.tab2 == None:
					Gtk.jenis = Gtk.tab2

			if Gtk.apa == 'merge':
				if len(varglo.skeleton_list)== 0:
					Gtk.apa = None
					Gtk.jenis = None

				else:
					if len(Gtk.jenis)<2:
						Gtk.apa = None
						Gtk.jenis = None
						print("    !!! merge need minimal need 2 skeleton")

			if Gtk.apa == 'edit':
				pass
 
			if Gtk.apa == 'undo':
				Gtk.jenis = Gtk.undo

			if Gtk.apa == 'clone':
				Gtk.jenis = Gtk.clone

			Gtk.main_quit()

		def on_tab_switched(self, notebook, current_page, page_num):

			jenispage = 'new smartkey'
			if len(varglo.smartkey_list)!=0:

				if page_num == 0:
					jenispage = 'edit'
					
				if page_num == 1:
					jenispage = 'new smartkey'

				if page_num == 2:
					jenispage = 'merge'

				if page_num == 3:
					jenispage = 'undo'

				if page_num == 4:
					if varglo.clone_layergroup == 'none':
						jenispage = None

					else:
						jenispage = 'clone'

			else:

				if page_num == 1:
					jenispage = 'merge'

				if page_num == 2:
					jenispage = 'undo'

				if page_num == 3:
					jenispage = 'clone'

			Gtk.apa = jenispage	

		def on_cancel_clicked(self, button):
			Gtk.apa = None
			Gtk.main_quit()

	print('    >>> show menu GTK')

	win = MyWindow()
	win.connect("destroy", Gtk.main_quit)
	Gtk.main()

	return Gtk.apa,Gtk.jenis,Gtk.wtemplate,Gtk.ikjenis
