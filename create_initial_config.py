import glob
import shutil

def main():
	files = glob.glob('sample_*.py')
	for file in files:
		new_file_name = file[7:]
		print ('Creating:'+ new_file_name)
		shutil.copyfile(file, new_file_name)

if __name__ == '__main__':
	main()