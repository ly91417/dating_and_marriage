# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-03-27 20:55:50
# @Last Modified by:   charlotte
# @Last Modified time: 2017-03-27 21:42:04

import py_entitymatching as em

def title_equiv(ltuple, rtuple):
    l_last_name = ltuple['name'].split()[1]
    r_last_name = rtuple['name'].split()[1]
    if l_last_name != r_last_name:
        return True
    else:
        return False

def year_equiv(ltuple, rtuple):
	l_year = ltuple['year']
	if not l_year:
		return False
	r_year = rtuple['year']
	if not r_year:
		return False
	print(l_year, r_year)
	return l_year == r_year

if __name__ == '__main__':

	A = em.read_csv_metadata('../managed_data/silicon_valley_dataset/songs_small.csv', key='id')
	B = em.read_csv_metadata('../managed_data/silicon_valley_dataset/tracks_small.csv', key='id')
	# ab = em.AttrEquivalenceBlocker()
	# C1 = ab.block_tables(A, B, 'year', 'year')

	# ob = em.OverlapBlocker()
	# C2 = ob.block_candset(C1, 'title', 'title', rem_stop_words=False, q_val=None, word_level=True, overlap_size=1, allow_missing=False, verbose=False, show_progress=True, n_jobs=1)

	# rb = em.RuleBasedBlocker()
	# rb.set_feature_table(em.get_features_for_blocking(A, B))
	# rule = ['title_equiv(ltuple, rtuple) == True']
	# rb.add_rule(rule, rule_name='title_equiv')

	bb = em.BlackBoxBlocker()
	bb.set_black_box_function(year_equiv)
	cands = bb.block_tables(A, B)
	print(cands)

