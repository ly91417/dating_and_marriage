import os, random, shutil as sh

def getRandomFile(path):
	files = os.listdir(path)
	index = random.randrange(0, len(files))
	return files[index]

def rand_selection(src, dst):
	for _ in range(100)
		fileName = getRandomFile(fileName)
		sh.move(src+fileName, dst+fileName)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='the source directory and the destination directory')
	parser.add_argument('-f', '--filename', type=str, help='Enter the output file name')
	rand_selection(src, dst)


