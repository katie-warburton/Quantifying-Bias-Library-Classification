'''
Helper code for tagging Library of Congress and Dewey Decimal nodes as western or non-western
based on a pre-defined set of starting nodes. 
'''

# Collect nodes in a subtree that are either western, non-western or neither.
# If west is True nodes are western, if west is False they are non-western,
# and if west is None they are neither. 
def parse_west_data(root, west, data):
    if root.west == west:
        data.append({'name': root.name,
                    'label': root.label,
                     'num_desc': root.count_descendants(),
                     'depth': root.depth,
                     'num_items': root.item_count,
                     'western': root.west,
                     'parent': root.parent,
                     'items': root.items})
    for child in root.children.values():
        if child is not None:
            parse_west_data(child, west, data)

# Function to tag a starting node and its children as western
# or non-western
def label(root, flag):
    root.west = flag
    for child in root.children.values():
        if child is not None:
            label(child, flag)

# Western non-western tagging assignments
def tag_lcc(tree):
    # RELIGION
    # Christianity
    root = tree.hash_table['B']['BR']['node']
    label(root, True)
    # Christian Denominations
    root = tree.hash_table['B']['BX']['node']
    label(root, True)
    # Judaism
    root = tree.hash_table['B']['BM']['node']
    label(root, True)
    # The bible
    root = tree.hash_table['B']['BS']['node']
    label(root, True)
    # Practical Theology
    root = tree.hash_table['B']['BV']['node']
    label(root, True)
    # Doctrinal Theology
    root = tree.hash_table['B']['BT']['node']
    label(root, True)
    # Religions. Mythology. Rationalism - subclass 'European. Occidental'
    root = tree.hash_table['B']['BL'][(689.0, 980.0)]
    label(root, True)
    # Religions. Mythology. Rationalism - subclass 'American'
    root = tree.hash_table['B']['BL'][(2500.0, 2592.0)]
    label(root, True)

    # Buddhism
    root = tree.hash_table['B']['BQ']['node']
    label(root, False)
    # Religions. Mythology. Rationalism - subclass 'Asian. Oriental'
    root = tree.hash_table['B']['BL'][(1000.0, 2370.0)]
    label(root, False)
    # Islam. Bahaism - (unsure)
    root = tree.hash_table['B']['BP']['node']
    label(root, False)
    # Religions. Mythology. Rationalism - subclass 'African'
    root = tree.hash_table['B']['BL'][(2390.0, 2490.0)]
    label(root, False)
    # Religions. Mythology. Rationalism - subclass 'Pacific Ocean islands.
    # Oceania'
    root = tree.hash_table['B']['BL'][(2600.0, 2630.0)]
    label(root, False)
    # Religions. Mythology. Rationalism - subclass 'Arctic Regions'
    root = tree.hash_table['B']['BL'][(2670.0, 2670.0)]
    label(root, False)
    # Religions. Mythology. Rationalism - subclass 'Ural-Altaic'
    root = tree.hash_table['B']['BL'][(685.0, 685.0)]
    label(root, False)

    # HISTORY
    # Great Britain -W
    root = tree.hash_table['D']['DA']['node']
    label(root, True)
    # Austria - Lichtenstein - Hungary - Czechoslovakia - W
    root = tree.hash_table['D']['DB']['node']
    label(root, True)
    # France - Andorra - Monaco - W
    root = tree.hash_table['D']['DC']['node']
    label(root, True)
    # Germany - W
    root = tree.hash_table['D']['DD']['node']
    label(root, True)
    # Greco-Roman World -W
    root = tree.hash_table['D']['DE']['node']
    label(root, True)
    # Greece - W
    root = tree.hash_table['D']['DF']['node']
    label(root, True)
    # Italy - Malta - W
    root = tree.hash_table['D']['DG']['node']
    label(root, True)
    # Low Countries - Benelux Countries - W
    root = tree.hash_table['D']['DH']['node']
    label(root, True)
    # Netherlands - W
    root = tree.hash_table['D']['DJ']['node']
    label(root, True)
    # Northern Europe. Scandinavia - W
    root = tree.hash_table['D']['DL']['node']
    label(root, True)
    # Spain - Portugal - W
    root = tree.hash_table['D']['DP']['node']
    label(root, True)
    # Switzerland - W
    root = tree.hash_table['D']['DQ']['node']
    label(root, True)
    # Oceania - Austrialia
    root = tree.hash_table['D']['DU'][(80.0, 398.0)]
    label(root, True)
    # Oceania - NZ
    root = tree.hash_table['D']['DU'][(400.0, 430.0)]
    label(root, True)
    # Central Europe
    root = tree.hash_table['D']['DAW']['node']
    label(root, True)
    # North + South America
    root = tree.hash_table['E']['node']
    label(root, True)  
    root = tree.hash_table['F']['node']
    label(root, True)  

    # Russia - NW
    root = tree.hash_table['D']['DK']['node']
    label(root, False)
    # Balkan Peninsula - NW
    root = tree.hash_table['D']['DR']['node']
    label(root, False)
    # Asia - NW
    root = tree.hash_table['D']['DS']['node']
    label(root, False)
    # Africa - NW
    root = tree.hash_table['D']['DT']['node']
    label(root, False)
    # Oceania - Melanesia
    root = tree.hash_table['D']['DU'][(490.0, 490.0)]
    label(root, False)
    # Oceania - Micronesia
    root = tree.hash_table['D']['DU'][(500.0, 500.0)]
    label(root, False)
    # Oceania - Polynesia
    root = tree.hash_table['D']['DU'][(510.0, 510.0)]
    label(root, False)
    # Oceania - Smaller island groups
    root = tree.hash_table['D']['DU'][(520.0, 950.0)]
    label(root, False)
    # Romanies - NW
    root = tree.hash_table['D']['DX']['node']
    label(root, False)
    # Eastern Europe
    root = tree.hash_table['D']['DJK']['node']
    label(root, False)
    
    # LANG + LIT
    # Greek/Latin lang + lit
    root = tree.hash_table['P']['PA']['node']
    label(root, True)
    # Germanic. Scandinavian Languages
    root = tree.hash_table['P']['PD']['node']
    label(root, True)
    # English language
    root = tree.hash_table['P']['PE']['node']
    label(root, True)
    # West germanic languages
    root = tree.hash_table['P']['PF']['node']
    label(root, True)
    # French, italian, spanish, portuguese lit
    root = tree.hash_table['P']['PQ']['node']
    label(root, True)
    # English lit
    root = tree.hash_table['P']['PR']['node']
    label(root, True)
    # American lit
    root = tree.hash_table['P']['PS']['node']
    label(root, True)
    # Modern languages. Celtic languages
    root = tree.hash_table['P']['PB']['node']
    label(root, True)
    # Romance langauges - (only uncertainty is Romanian)
    root = tree.hash_table['P']['PC']['node']
    label(root, True)
    # Uralic + Basque langauges
    root = tree.hash_table['P']['PH']['node']
    label(root, True)
    # Baltic languages
    root = tree.hash_table['P']['PG'][(8001.0, 9146.0)]
    label(root, True)

    # Oriental lang + lit
    root = tree.hash_table['P']['PJ']['node']
    label(root, False)
    # Lang + Lit of east Asia, Africa, Oceania
    root = tree.hash_table['P']['PL']['node']
    label(root, False)
    # Indo-Iranian languages
    root = tree.hash_table['P']['PK']['node']
    label(root, False)
    # Albanian
    root = tree.hash_table['P']['PG'][(9501.0, 9665.0)]
    label(root, False)
    # Slavic langauges - some exceptions might need to be dealt with
    root = tree.hash_table['P']['PG'][(1.0, 7925.0)]
    label(root, False)
    # Hperborean languages of Arctic Asia and America
    root = tree.hash_table['P']['PM'][(1.0, 94.0)]
    label(root, False)
    # American languages (Aboriginal)
    root = tree.hash_table['P']['PM'][(101.0, 2711.0)]
    label(root, False)
    # Languages of Mexico and Central America - assumption (refers to
    # indigenous languages)
    root = tree.hash_table['P']['PM'][(3001.0, 4566.0)]
    label(root, False)
    # Languages of South America and the West Indies - same assumption as above
    root = tree.hash_table['P']['PM'][(5001.0, 7356.0)]
    label(root, False)


def tag_dewey(tree):
    # HISTORY
    # British Isles
    node = tree.get_node('941')
    label(node, True)
    # England and Wales
    node = tree.get_node('942')
    label(node, True)
    # Germany
    node = tree.get_node('943')
    label(node, True)
    # France + Monaco
    node = tree.get_node('944')
    label(node, True)
    # Italy + Malta
    node = tree.get_node('945')
    label(node, True)
    # Spain
    node = tree.get_node('946')
    label(node, True)
    # Scandinavia
    node = tree.get_node('948')
    label(node, True)
    # History of North America
    node = tree.get_node('97')
    label(node, True)
    # History of South America
    node = tree.get_node('98')
    label(node, True)
    # New Zealand
    node = tree.get_node('993')
    label(node, True)
    # Austrailia
    node = tree.get_node('994')
    label(node, True)

    # Russia
    node = tree.get_node('947')
    label(node, False)
    # History of Asia
    node = tree.get_node('95')
    label(node, False)
    # History of Africa
    node = tree.get_node('96')
    label(node, False)
    # New Guinea
    node = tree.get_node('995')
    label(node, False)
    # Polynesia
    node = tree.get_node('996')
    label(node, False)
    # Malaysia, Indonesia, Philippines (used to be - now unnasigned)
    node = tree.get_node('991')
    label(node, False)
    # Malaysia, Indonesia (used to be - now unnasigned)
    node = tree.get_node('992')
    label(node, False)

    # RELIGION
    # The Bible
    node = tree.get_node('22')
    label(node, True)
    # Christianity
    node = tree.get_node('23')
    label(node, True)
    # Christian practices
    node = tree.get_node('24')
    label(node, True)
    # Christian orders
    node = tree.get_node('25')
    label(node, True)
    #  Social + ecclesiatical theology
    node = tree.get_node('26')
    label(node, True)
    # History of Christianity
    node = tree.get_node('27')
    label(node, True)
    # Chrisitan Denominations
    node = tree.get_node('28')
    label(node, True)
    # Scientology
    node = tree.get_node('299.936')
    label(node, True)

    # Religions of Indic Origin
    node = tree.get_node('294')
    label(node, False)
    # Zoroastrianism
    node = tree.get_node('295')
    label(node, False)
    # Judaism
    node = tree.get_node('296')
    label(node, True)
    # Islam, Babism, Bahai
    node = tree.get_node('297')
    label(node, False)
    # Sumer, Assyria, Mesopotamia
    node = tree.get_node('299.2')
    label(node, False)
    # North African Origin
    node = tree.get_node('299.3')
    label(node, False)
    # Eurasian Origin
    node = tree.get_node('299.4')
    label(node, False)
    # Asian Origin
    node = tree.get_node('299.5')
    label(node, False)
    # African Origin
    node = tree.get_node('299.6')
    label(node, False)
    # North American Origin
    node = tree.get_node('299.7')
    label(node, False)
    # South American
    node = tree.get_node('299.8')
    label(node, False)
    # Pacific or Other Ethnic Origin
    node = tree.get_node('299.92')
    label(node, False)

    # LANG + LIT
    # English
    node = tree.get_node('42')
    label(node, True)
    # German & Germanic Languages
    node = tree.get_node('43')
    label(node, True)
    # French and Related Languages
    node = tree.get_node('44')
    label(node, True)
    # Italian, Romanian & related languages
    node = tree.get_node('45')
    label(node, True)
    # Spanish & Portuguese languages
    node = tree.get_node('46')
    label(node, True)
    # Latin and Italic Languages
    node = tree.get_node('47')
    label(node, True)
    # Classical & modern Greek languages
    node = tree.get_node('48')
    label(node, True)
    # Celtic
    node = tree.get_node('491.6')
    label(node, True)
    # Baltic
    node = tree.get_node('491.9')
    label(node, True)
    # Finno-Ugric
    node = tree.get_node('494.5')
    label(node, True)
    # English (North America)
    node = tree.get_node('81')
    label(node, True)
    # English (except North America)
    node = tree.get_node('82')
    label(node, True)
    # German & Germanic
    node = tree.get_node('83')
    label(node, True)
    # French
    node = tree.get_node('84')
    label(node, True)
    # Italian
    node = tree.get_node('85')
    label(node, True)
    # Spanish & Portuguese
    node = tree.get_node('86')
    label(node, True)
    # Latin
    node = tree.get_node('87')
    label(node, True)
    # Greek & other classical languages
    node = tree.get_node('88')
    label(node, True)
    # Celtic languages
    node = tree.get_node('891.6')
    label(node, True)
    # Old Prussian
    node = tree.get_node('891.91')
    label(node, True)
    # Lithuanian lit
    node = tree.get_node('891.92')
    label(node, True)
    # Latvian lit
    node = tree.get_node('891.93')
    label(node, True)
    # Fenno-Ugric lit
    node = tree.get_node('894.5')
    label(node, True)

    # African Languages
    node = tree.get_node('496')
    label(node, False)
    # North American Native Languages
    node = tree.get_node('497')
    label(node, False)
    # South American Native Languages
    node = tree.get_node('498')
    label(node, False)
    # Austronesian & Other Languages
    node = tree.get_node('499')
    label(node, False)
    # Languages of East and Southeast Asia
    node = tree.get_node('495')
    label(node, False)
    # Non-Semitic Afro-Asiatic languages
    node = tree.get_node('493')
    label(node, False)
    # Afro-Asiatic languages; Semitic languages
    node = tree.get_node('492')
    label(node, False)
    # Indic
    node = tree.get_node('491.1')
    label(node, False)
    # Sanskrit
    node = tree.get_node('491.2')
    label(node, False)
    # Pali
    node = tree.get_node('491.3')
    label(node, False)
    # Modern East Indian languages
    node = tree.get_node('491.4')
    label(node, False)
    # Iranic
    node = tree.get_node('491.5')
    label(node, False)
    # Russian +
    node = tree.get_node('491.7')
    label(node, False)
    # Slavic languages
    node = tree.get_node('491.8')
    label(node, False)
    # Mongolian
    node = tree.get_node('494.2')
    label(node, False)
    # Turkish
    node = tree.get_node('494.3')
    label(node, False)
    # East Altaic languages
    node = tree.get_node('494.6')
    label(node, False)
    # Dravidian languages
    node = tree.get_node('494.8')
    label(node, False)
    # Middle Eastern languages
    node = tree.get_node('892')
    label(node, False)
    # Lit. of Egyptian, Coptic and North African langs
    node = tree.get_node('893')
    label(node, False)
    # Asian languages
    node = tree.get_node('895')
    label(node, False)
    # African languages
    node = tree.get_node('896')
    label(node, False)
    # North American native languages
    node = tree.get_node('897')
    label(node, False)
    # South American native languages
    node = tree.get_node('898')
    label(node, False)
    # Indo-Iranian
    node = tree.get_node('891.1')
    label(node, False)
    # Sanskrit
    node = tree.get_node('891.2')
    label(node, False)
    # Middle Indic Languages
    node = tree.get_node('891.3')
    label(node, False)
    # Modern Indic Languages
    node = tree.get_node('891.4')
    label(node, False)
    # Persian
    node = tree.get_node('891.5')
    label(node, False)
    # Russian and East Slavic Languages
    node = tree.get_node('891.7')
    label(node, False)
    # West + South Slavic Languages
    node = tree.get_node('891.8')
    label(node, False)
    # Tungusic Languages
    node = tree.get_node('894.1')
    label(node, False)
    # Mongolic
    node = tree.get_node('894.2')
    label(node, False)
    # Turkic
    node = tree.get_node('894.3')
    label(node, False)
    # Paleosiberian
    node = tree.get_node('894.6')
    label(node, False)
    # Dravidian
    node = tree.get_node('894.8')
    label(node, False)
    # Other Indo-European languages
    node = tree.get_node('891.99')
    label(node, False)
    # Other lit
    node = tree.get_node('899')
    label(node, False)
