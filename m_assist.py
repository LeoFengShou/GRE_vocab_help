import json
import argparse
import glob
import os
import random
import datetime


# occurance_for_mastering = 5


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--docs_folder", help = "The folder containing the files of vocabulary. default is vocabulary", default = "vocabulary")
	parser.add_argument("--doc_glob", help = "The glob expression defining all the vocabulary files. default is *.txt", default = "*.txt")
	parser.add_argument("--intermediate", help = "Indicated whether picks up from the last stop point. default is Y", default = "Y")
	parser.add_argument("--occurance_for_mastering", help = "The number of times checked for the review list, default is 5", default = 5)
	args = parser.parse_args()
	# print(isinstance(occurance_for_mastering, int))
	# print(occurance_for_mastering)
	memorize(args.docs_folder, args.doc_glob, args.intermediate, args.occurance_for_mastering)


def memorize(docs_folder, doc_glob, intermediate, occurance_for_mastering):
	if not os.path.exists(docs_folder):
		print(docs_folder + " is not present as a folder in the cwd")
		return
	intermediate_file = glob.glob(docs_folder + "/intermediate_*.json")
	if (intermediate == "Y" or intermediate == "Yes" or intermediate == "yes" or intermediate == "y") and len(intermediate_file) != 0:
		with open(intermediate_file[0], "r") as inte_in:
			all_voca = json.load(inte_in)
	else:
		all_voca = load_from_raw(docs_folder, doc_glob)
	# print(all_voca)
	interact(all_voca, docs_folder, occurance_for_mastering)


def interact(all_voca, docs_folder, occurance_for_mastering):
	use_in = "start, occurance_for_mastering"
	while use_in != "exit" and (len(all_voca["learning"]) != 0 or len(all_voca["review"]) != 0):
		rand = random.random()
		if rand > 0.75:
			use_in = check_one_word_from_list(all_voca, "known", occurance_for_mastering)
		if rand > 0.5:
			use_in = check_one_word_from_list(all_voca, "review", occurance_for_mastering)
		use_in = check_one_word_from_list(all_voca, "learning", occurance_for_mastering)
		# print("haha")
	now = datetime.datetime.now()
	if use_in == "exit":
		# Store the process 
		with open(docs_folder + "/intermediate_" + now.strftime("%Y%m%d") + ".json", "w") as process_out:
			json.dump(all_voca, process_out, indent=4, sort_keys=True)
	if len(all_voca["learning"]) == 0:
		# Go through all the vocabulary again
		for word in all_voca["learning"]:
			use_in = input("\nTap to see the meaning of the word \" \t\t\t" + word["word"] + "\t\t\t \" in " + "learning" + " list")
			if use_in == "exit":
				return 
			print("\n" + word["meaning"] + "\n")
		return


def check_one_word_from_list(all_voca, cate, occurance_for_mastering):
	# Return whether the user knows the word or not, update the count
	lis = all_voca[cate]
	if len(lis) < 1:
		return
	index = int(random.random() * len(lis))
	if index == len(lis):
		index -= 1
	if cate == "known" and lis[index]["count"] == occurance_for_mastering:
		return 
	try:
		use_in = input("\nTap to see the meaning of the word \" \t\t\t" + lis[index]["word"] + "\t\t\t \" in " + cate + " list:")
		if use_in == "exit":
			return "exit"
	except:
		import pdb; pdb.set_trace()
	print("\n\t\t\t" + lis[index]["meaning"] + "\n")
	use_in = input("Do you know the meaning of the word?")
	if use_in == "exit":
		return "exit"
	if use_in in ["Y", "yes", "Yes", "y", "ok", "OK"]:
		if cate == "learning":
			lis[index]["count"] = 0
			all_voca["review"].append(lis[index])
			all_voca["learning"].remove(lis[index])
		if cate == "review":
			if lis[index]["count"] < occurance_for_mastering:
				lis[index]["count"] += 1
			else:
				lis[index]["count"] = 0
				all_voca["known"].append(lis[index])
				all_voca["review"].remove(lis[index])
		if cate == "known":
			lis[index]["count"] += 1
	else:
		if cate == "known" or cate == "review":
			lis[index]["count"] = -1
			all_voca["learning"].append(lis[index])
			all_voca[cate].remove(lis[index])


def load_from_raw(docs_folder, doc_glob):
	all_raw_files = glob.glob(docs_folder + "/" + doc_glob)
	# {"known": [{"word": "today", "count": 0, "meaning": "..."}], "review": [{}], "learning": [{}]} 
	# The first time all words are loaded into the learning list
	all_voca = {"known": [], "review": [], "learning": []} 
	for raw_file in all_raw_files:
		try:
			words = [word for word in open(raw_file, "r").read().split("\n") if word]
		except:
			import pdb; pdb.set_trace()
		for word in words:
			word_spell = word[ : word.find(":")]
			word_mean = word[word.find(":") + 1 : ]
			all_voca["learning"].append({"word": word_spell, "count": -1, "meaning": word_mean})
	return all_voca


if __name__ == '__main__':
	main()