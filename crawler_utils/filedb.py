#!/usr/bin/env python3
'''
**********************************************************************
* Filename    : filedb.py
* Description : A simple file based database.
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
**********************************************************************
'''
import os
from time import sleep
from typing import Optional, Union


class fileDB(object):
	"""A file based database.

    A file based database, read and write arguements in the specific file.
    """
	def __init__(self, db: str, mode: Optional[str] = None, owner: Optional[str] = None):  
		'''
		Init the db_file is a file to save the datas.
		
		:param db: the file to save the datas.
		:type db: str
		:param mode: the mode of the file.
		:type mode: str
		:param owner: the owner of the file.
		:type owner: str
		'''

		self.db = db
		# Check if db_file is existed, otherwise create one
		if self.db != None:	
			self.file_check_create(db, mode, owner)
		else:
			raise ValueError('db: Missing file path parameter.')


	def file_check_create(self, file_path: str, mode: Optional[str] = None, owner: Optional[str] = None):
		"""
		Check if file is existed, otherwise create one.
		
		:param file_path: the file to check
		:type file_path: str
		:param mode: the mode of the file.
		:type mode: str
		:param owner: the owner of the file.
		:type owner: str
		"""
		dir = file_path.rsplit('/',1)[0]
		try:
			if os.path.exists(file_path):
				if not os.path.isfile(file_path):
					print('Could not create file, there is a folder with the same name')
					return
			else:
				if os.path.exists(dir):
					if not os.path.isdir(dir):
						print('Could not create directory, there is a file with the same name')
						return
				else:
					os.makedirs(file_path.rsplit('/',1)[0], mode=0o754)
					sleep(0.001)

				with open(file_path, 'w') as f:
					f.write("# robot-hat config and calibration value of robots\n\n")

			if mode is not None:
				os.chmod(file_path, int(mode, 8))

			if owner is not None:
				try:
					import pwd, grp
					uid = pwd.getpwnam(owner).pw_uid
					gid = grp.getgrnam(owner).gr_gid
					os.chown(file_path, uid, gid)
				except Exception:
					pass
		except Exception as e:
			raise(e) 
	
	def get(self, name: str, default_value: Union[str, int] = 0) -> Union[str, int]:
		"""
		Get value with data's name
		
		:param name: the name of the arguement
		:type name: str
		:param default_value: the default value of the arguement
		:type default_value: str
		:return: the value of the arguement
		:rtype: str
		"""
		try:
			conf = open(self.db,'r')
			lines=conf.readlines()
			conf.close()
			file_len=len(lines)-1
			flag = False
			value = default_value
			# Find the arguement and set the value
			for i in range(file_len):
				if lines[i][0] != '#':
					if lines[i].split('=')[0].strip() == name:
						value = lines[i].split('=')[1].replace(' ', '').strip()
						flag = True
			if flag:
				return value

			return 0

		except FileNotFoundError:
			conf = open(self.db,'w')
			conf.write("")
			conf.close()
			return 0
		except :
			return 0
	
	def set(self, name, value):
		"""
		Set value by with name. Or create one if the arguement does not exist
		
		:param name: the name of the arguement
		:type name: str
		:param value: the value of the arguement
		:type value: str
		"""
		# Read the file
		conf = open(self.db,'r')
		lines=conf.readlines()
		conf.close()
		file_len=len(lines)-1
		flag = False
		# Find the arguement and set the value
		for i in range(file_len):
			if lines[i][0] != '#':
				if lines[i].split('=')[0].strip() == name:
					lines[i] = '%s = %s\n' % (name, value)
					flag = True
		# If arguement does not exist, create one
		if not flag:
			lines.append('%s = %s\n\n' % (name, value))

		# Save the file
		conf = open(self.db,'w')
		conf.writelines(lines)
		conf.close()
