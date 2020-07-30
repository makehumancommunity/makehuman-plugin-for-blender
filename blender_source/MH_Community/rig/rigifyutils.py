import bpy, bmesh
from ..util import bl28
from pprint import pprint

_SIDEDMATCHES = dict()

# Arm
_SIDEDMATCHES["shoulder.#"] = dict()
_SIDEDMATCHES["shoulder.#"]["head"] = "joint-#-clavicle"
_SIDEDMATCHES["shoulder.#"]["tail"] = "joint-#-scapula"
_SIDEDMATCHES["upper_arm.#"] = dict()
_SIDEDMATCHES["upper_arm.#"]["head"] = "joint-#-shoulder"
_SIDEDMATCHES["upper_arm.#"]["tail"] = "joint-#-elbow"
_SIDEDMATCHES["forearm.#"] = dict()
_SIDEDMATCHES["forearm.#"]["head"] = "joint-#-elbow"
_SIDEDMATCHES["forearm.#"]["tail"] = "joint-#-hand"
_SIDEDMATCHES["hand.#"] = dict()
_SIDEDMATCHES["hand.#"]["head"] = "joint-#-hand"
_SIDEDMATCHES["hand.#"]["tail"] = "joint-#-hand-3"

# Finger 5 (pinky)
_SIDEDMATCHES["palm.04.#"] = dict()
_SIDEDMATCHES["palm.04.#"]["head"] = "joint-#-hand-2"
_SIDEDMATCHES["palm.04.#"]["tail"] = "joint-#-finger-5-1"

_SIDEDMATCHES["f_pinky.01.#"] = dict()
_SIDEDMATCHES["f_pinky.01.#"]["head"] = "joint-#-finger-5-1"
_SIDEDMATCHES["f_pinky.01.#"]["tail"] = "joint-#-finger-5-2"

_SIDEDMATCHES["f_pinky.02.#"] = dict()
_SIDEDMATCHES["f_pinky.02.#"]["head"] = "joint-#-finger-5-2"
_SIDEDMATCHES["f_pinky.02.#"]["tail"] = "joint-#-finger-5-3"

_SIDEDMATCHES["f_pinky.03.#"] = dict()
_SIDEDMATCHES["f_pinky.03.#"]["head"] = "joint-#-finger-5-3"
_SIDEDMATCHES["f_pinky.03.#"]["tail"] = "joint-#-finger-5-4"

_SIDEDMATCHES["f_pinky.04.#"] = dict()
_SIDEDMATCHES["f_pinky.04.#"]["head"] = "joint-#-finger-5-4"
_SIDEDMATCHES["f_pinky.04.#"]["tail"] = "joint-#-finger-5-5"

# Finger 4 (ring)
_SIDEDMATCHES["palm.03.#"] = dict()
_SIDEDMATCHES["palm.03.#"]["head"] = "joint-#-hand-2"
_SIDEDMATCHES["palm.03.#"]["tail"] = "joint-#-finger-4-1"

_SIDEDMATCHES["f_ring.01.#"] = dict()
_SIDEDMATCHES["f_ring.01.#"]["head"] = "joint-#-finger-4-1"
_SIDEDMATCHES["f_ring.01.#"]["tail"] = "joint-#-finger-4-2"

_SIDEDMATCHES["f_ring.02.#"] = dict()
_SIDEDMATCHES["f_ring.02.#"]["head"] = "joint-#-finger-4-2"
_SIDEDMATCHES["f_ring.02.#"]["tail"] = "joint-#-finger-4-3"

_SIDEDMATCHES["f_ring.03.#"] = dict()
_SIDEDMATCHES["f_ring.03.#"]["head"] = "joint-#-finger-4-3"
_SIDEDMATCHES["f_ring.03.#"]["tail"] = "joint-#-finger-4-4"

_SIDEDMATCHES["f_ring.04.#"] = dict()
_SIDEDMATCHES["f_ring.04.#"]["head"] = "joint-#-finger-4-4"
_SIDEDMATCHES["f_ring.04.#"]["tail"] = "joint-#-finger-4-5"

# Finger 3 (middle)
_SIDEDMATCHES["palm.02.#"] = dict()
_SIDEDMATCHES["palm.02.#"]["head"] = "joint-#-hand-3"
_SIDEDMATCHES["palm.02.#"]["tail"] = "joint-#-finger-3-1"

_SIDEDMATCHES["f_middle.01.#"] = dict()
_SIDEDMATCHES["f_middle.01.#"]["head"] = "joint-#-finger-3-1"
_SIDEDMATCHES["f_middle.01.#"]["tail"] = "joint-#-finger-3-2"

_SIDEDMATCHES["f_middle.02.#"] = dict()
_SIDEDMATCHES["f_middle.02.#"]["head"] = "joint-#-finger-3-2"
_SIDEDMATCHES["f_middle.02.#"]["tail"] = "joint-#-finger-3-3"

_SIDEDMATCHES["f_middle.03.#"] = dict()
_SIDEDMATCHES["f_middle.03.#"]["head"] = "joint-#-finger-3-3"
_SIDEDMATCHES["f_middle.03.#"]["tail"] = "joint-#-finger-3-4"

_SIDEDMATCHES["f_middle.04.#"] = dict()
_SIDEDMATCHES["f_middle.04.#"]["head"] = "joint-#-finger-3-4"
_SIDEDMATCHES["f_middle.04.#"]["tail"] = "joint-#-finger-3-5"

# Finger 2 (index)
_SIDEDMATCHES["palm.01.#"] = dict()
_SIDEDMATCHES["palm.01.#"]["head"] = "joint-#-hand-3"
_SIDEDMATCHES["palm.01.#"]["tail"] = "joint-#-finger-2-1"

_SIDEDMATCHES["f_index.01.#"] = dict()
_SIDEDMATCHES["f_index.01.#"]["head"] = "joint-#-finger-2-1"
_SIDEDMATCHES["f_index.01.#"]["tail"] = "joint-#-finger-2-2"

_SIDEDMATCHES["f_index.02.#"] = dict()
_SIDEDMATCHES["f_index.02.#"]["head"] = "joint-#-finger-2-2"
_SIDEDMATCHES["f_index.02.#"]["tail"] = "joint-#-finger-2-3"

_SIDEDMATCHES["f_index.03.#"] = dict()
_SIDEDMATCHES["f_index.03.#"]["head"] = "joint-#-finger-2-3"
_SIDEDMATCHES["f_index.03.#"]["tail"] = "joint-#-finger-2-4"

_SIDEDMATCHES["f_index.04.#"] = dict()
_SIDEDMATCHES["f_index.04.#"]["head"] = "joint-#-finger-2-4"
_SIDEDMATCHES["f_index.04.#"]["tail"] = "joint-#-finger-2-5"

# Finger 1 (thumb)
_SIDEDMATCHES["thumb.01.#"] = dict()
_SIDEDMATCHES["thumb.01.#"]["head"] = "joint-#-finger-1-1"
_SIDEDMATCHES["thumb.01.#"]["tail"] = "joint-#-finger-1-2"

_SIDEDMATCHES["thumb.02.#"] = dict()
_SIDEDMATCHES["thumb.02.#"]["head"] = "joint-#-finger-1-2"
_SIDEDMATCHES["thumb.02.#"]["tail"] = "joint-#-finger-1-3"

_SIDEDMATCHES["thumb.03.#"] = dict()
_SIDEDMATCHES["thumb.03.#"]["head"] = "joint-#-finger-1-3"
_SIDEDMATCHES["thumb.03.#"]["tail"] = "joint-#-finger-1-4"

_SIDEDMATCHES["thumb.04.#"] = dict()
_SIDEDMATCHES["thumb.04.#"]["head"] = "joint-#-finger-1-4"
_SIDEDMATCHES["thumb.04.#"]["tail"] = "joint-#-finger-1-5"

# Leg

_SIDEDMATCHES["thigh.#"] = dict()
_SIDEDMATCHES["thigh.#"]["head"] = "joint-#-upper-leg"
_SIDEDMATCHES["thigh.#"]["tail"] = "joint-#-knee"

_SIDEDMATCHES["shin.#"] = dict()
_SIDEDMATCHES["shin.#"]["head"] = "joint-#-knee"
_SIDEDMATCHES["shin.#"]["tail"] = "joint-#-ankle"

_SIDEDMATCHES["foot.#"] = dict()
_SIDEDMATCHES["foot.#"]["head"] = "joint-#-ankle"
_SIDEDMATCHES["foot.#"]["tail"] = "joint-#-foot-1"

_SIDEDMATCHES["toe.#"] = dict()
_SIDEDMATCHES["toe.#"]["head"] = "joint-#-foot-1"
_SIDEDMATCHES["toe.#"]["tail"] = "joint-#-foot-2"

# Eye

_SIDEDMATCHES["eye.#"] = dict()
_SIDEDMATCHES["eye.#"]["head"] = "joint-#-eye"
_SIDEDMATCHES["eye.#"]["tail"] = "joint-#-eye-target"


_BONEMATCHER = dict()

# Spine
_BONEMATCHER["spine"] = dict()
_BONEMATCHER["spine"]["head"] = "joint-pelvis"
_BONEMATCHER["spine"]["tail"] = "joint-spine-4"
_BONEMATCHER["spine.001"] = dict()
_BONEMATCHER["spine.001"]["head"] = "joint-spine-4"
_BONEMATCHER["spine.001"]["tail"] = "joint-spine-3"
_BONEMATCHER["spine.002"] = dict()
_BONEMATCHER["spine.002"]["head"] = "joint-spine-3"
_BONEMATCHER["spine.002"]["tail"] = "joint-spine-2"
_BONEMATCHER["spine.003"] = dict()
_BONEMATCHER["spine.003"]["head"] = "joint-spine-2"
_BONEMATCHER["spine.003"]["tail"] = "joint-spine-1"
_BONEMATCHER["spine.004"] = dict()
_BONEMATCHER["spine.004"]["head"] = "joint-spine-1"
_BONEMATCHER["spine.004"]["tail"] = "joint-neck"
_BONEMATCHER["spine.005"] = dict()
_BONEMATCHER["spine.005"]["head"] = "joint-neck"
_BONEMATCHER["spine.005"]["tail"] = "joint-head"
_BONEMATCHER["spine.006"] = dict()
_BONEMATCHER["spine.006"]["head"] = "joint-head"
_BONEMATCHER["spine.006"]["tail"] = "joint-head-2"

# Face meta bone - same place but half the height of spine.006
_BONEMATCHER["face"] = dict()
_BONEMATCHER["face"]["head"] = "joint-head"
_BONEMATCHER["face"]["tail"] = "joint-head | joint-head-2"

# Heel rollers
_BONEMATCHER["heel.02.R"] = dict()
_BONEMATCHER["heel.02.R"]["head"] = 15455
_BONEMATCHER["heel.02.R"]["tail"] = 15452
_BONEMATCHER["heel.02.L"] = dict()
_BONEMATCHER["heel.02.L"]["head"] = 16759
_BONEMATCHER["heel.02.L"]["tail"] = 16756

# Pelvis movers
_BONEMATCHER["pelvis.R"] = dict()
_BONEMATCHER["pelvis.R"]["head"] = "joint-pelvis"
_BONEMATCHER["pelvis.R"]["tail"] = 4284
_BONEMATCHER["pelvis.L"] = dict()
_BONEMATCHER["pelvis.L"]["head"] = "joint-pelvis"
_BONEMATCHER["pelvis.L"]["tail"] = 10914

# Breast
_BONEMATCHER["breast.R"] = dict()
_BONEMATCHER["breast.R"]["head"] = 3956
_BONEMATCHER["breast.R"]["tail"] = 1764
_BONEMATCHER["breast.L"] = dict()
_BONEMATCHER["breast.L"]["head"] = 10619
_BONEMATCHER["breast.L"]["tail"] = 8436

# Lips

_BONEMATCHER["lip.T.R"] = dict()
_BONEMATCHER["lip.T.R"]["head"] = 467
_BONEMATCHER["lip.T.R"]["tail"] = 5352
_BONEMATCHER["lip.T.R.001"] = dict()
_BONEMATCHER["lip.T.R.001"]["head"] = 5352
_BONEMATCHER["lip.T.R.001"]["tail"] = 425

_BONEMATCHER["lip.T.L"] = dict()
_BONEMATCHER["lip.T.L"]["head"] = 467
_BONEMATCHER["lip.T.L"]["tail"] = 11954
_BONEMATCHER["lip.T.L.001"] = dict()
_BONEMATCHER["lip.T.L.001"]["head"] = 11954
_BONEMATCHER["lip.T.L.001"]["tail"] = 7185

_BONEMATCHER["lip.B.R"] = dict()
_BONEMATCHER["lip.B.R"]["head"] = 495
_BONEMATCHER["lip.B.R"]["tail"] = 483
_BONEMATCHER["lip.B.R.001"] = dict()
_BONEMATCHER["lip.B.R.001"]["head"] = 483
_BONEMATCHER["lip.B.R.001"]["tail"] = 425
_BONEMATCHER["ear.R.001"] = dict()
_BONEMATCHER["ear.R.001"]["head"] = 467
_BONEMATCHER["ear.R.001"]["tail"] = 5352

_BONEMATCHER["lip.B.L"] = dict()
_BONEMATCHER["lip.B.L"]["head"] = 495
_BONEMATCHER["lip.B.L"]["tail"] = 7283
_BONEMATCHER["lip.B.L.001"] = dict()
_BONEMATCHER["lip.B.L.001"]["head"] = 7238
_BONEMATCHER["lip.B.L.001"]["tail"] = 7185

# Ears

_BONEMATCHER["ear.R"] = dict()
_BONEMATCHER["ear.R"]["head"] = 5456
_BONEMATCHER["ear.R"]["tail"] = 5447
_BONEMATCHER["ear.R.001"] = dict()
_BONEMATCHER["ear.R.001"]["head"] = 5447
_BONEMATCHER["ear.R.001"]["tail"] = 5438
_BONEMATCHER["ear.R.002"] = dict()
_BONEMATCHER["ear.R.002"]["head"] = 5438
_BONEMATCHER["ear.R.002"]["tail"] = 5462
_BONEMATCHER["ear.R.003"] = dict()
_BONEMATCHER["ear.R.003"]["head"] = 5462
_BONEMATCHER["ear.R.003"]["tail"] = 5420
_BONEMATCHER["ear.R.004"] = dict()
_BONEMATCHER["ear.R.004"]["head"] = 5420
_BONEMATCHER["ear.R.004"]["tail"] = 5465

_BONEMATCHER["ear.L"] = dict()
_BONEMATCHER["ear.L"]["head"] = 12064
_BONEMATCHER["ear.L"]["tail"] = 12055
_BONEMATCHER["ear.L.001"] = dict()
_BONEMATCHER["ear.L.001"]["head"] = 12055
_BONEMATCHER["ear.L.001"]["tail"] = 12046
_BONEMATCHER["ear.L.002"] = dict()
_BONEMATCHER["ear.L.002"]["head"] = 12046
_BONEMATCHER["ear.L.002"]["tail"] = 12037
_BONEMATCHER["ear.L.003"] = dict()
_BONEMATCHER["ear.L.003"]["head"] = 12037
_BONEMATCHER["ear.L.003"]["tail"] = 12061
_BONEMATCHER["ear.L.004"] = dict()
_BONEMATCHER["ear.L.004"]["head"] = 12061
_BONEMATCHER["ear.L.004"]["tail"] = 12019

# Eyebrow right side top/bottom

_BONEMATCHER["brow.T.R"] = dict()
_BONEMATCHER["brow.T.R"]["head"] = 263
_BONEMATCHER["brow.T.R"]["tail"] = 254
_BONEMATCHER["brow.T.R.001"] = dict()
_BONEMATCHER["brow.T.R.001"]["head"] = 254
_BONEMATCHER["brow.T.R.001"]["tail"] = 206
_BONEMATCHER["brow.T.R.002"] = dict()
_BONEMATCHER["brow.T.R.002"]["head"] = 206
_BONEMATCHER["brow.T.R.002"]["tail"] = 208
_BONEMATCHER["brow.T.R.003"] = dict()
_BONEMATCHER["brow.T.R.003"]["head"] = 208
_BONEMATCHER["brow.T.R.003"]["tail"] = 132

_BONEMATCHER["brow.B.R"] = dict()
_BONEMATCHER["brow.B.R"]["head"] = 188
_BONEMATCHER["brow.B.R"]["tail"] = 160
_BONEMATCHER["brow.B.R.001"] = dict()
_BONEMATCHER["brow.B.R.001"]["head"] = 160
_BONEMATCHER["brow.B.R.001"]["tail"] = 172
_BONEMATCHER["brow.B.R.002"] = dict()
_BONEMATCHER["brow.B.R.002"]["head"] = 172
_BONEMATCHER["brow.B.R.002"]["tail"] = 174
_BONEMATCHER["brow.B.R.003"] = dict()
_BONEMATCHER["brow.B.R.003"]["head"] = 174
_BONEMATCHER["brow.B.R.003"]["tail"] = 166

# Eyebrow left side top/bottom

_BONEMATCHER["brow.T.L"] = dict()
_BONEMATCHER["brow.T.L"]["head"] = 7032
_BONEMATCHER["brow.T.L"]["tail"] = 7023
_BONEMATCHER["brow.T.L.001"] = dict()
_BONEMATCHER["brow.T.L.001"]["head"] = 7023
_BONEMATCHER["brow.T.L.001"]["tail"] = 6981
_BONEMATCHER["brow.T.L.002"] = dict()
_BONEMATCHER["brow.T.L.002"]["head"] = 6981
_BONEMATCHER["brow.T.L.002"]["tail"] = 6983
_BONEMATCHER["brow.T.L.003"] = dict()
_BONEMATCHER["brow.T.L.003"]["head"] = 6983
_BONEMATCHER["brow.T.L.003"]["tail"] = 132

_BONEMATCHER["brow.B.L"] = dict()
_BONEMATCHER["brow.B.L"]["head"] = 6964
_BONEMATCHER["brow.B.L"]["tail"] = 6938
_BONEMATCHER["brow.B.L.001"] = dict()
_BONEMATCHER["brow.B.L.001"]["head"] = 6938
_BONEMATCHER["brow.B.L.001"]["tail"] = 6948
_BONEMATCHER["brow.B.L.002"] = dict()
_BONEMATCHER["brow.B.L.002"]["head"] = 6948
_BONEMATCHER["brow.B.L.002"]["tail"] = 6950
_BONEMATCHER["brow.B.L.003"] = dict()
_BONEMATCHER["brow.B.L.003"]["head"] = 6950
_BONEMATCHER["brow.B.L.003"]["tail"] = 6943

# Cheek

_BONEMATCHER["cheek.T.R"] = dict()
_BONEMATCHER["cheek.T.R"]["head"] = 263
_BONEMATCHER["cheek.T.R"]["tail"] = 5133
_BONEMATCHER["cheek.T.R.001"] = dict()
_BONEMATCHER["cheek.T.R.001"]["head"] = 5133
_BONEMATCHER["cheek.T.R.001"]["tail"] = 5100

_BONEMATCHER["cheek.B.R"] = dict()
_BONEMATCHER["cheek.B.R"]["head"] = 425
_BONEMATCHER["cheek.B.R"]["tail"] = 5153
_BONEMATCHER["cheek.B.R.001"] = dict()
_BONEMATCHER["cheek.B.R.001"]["head"] = 5153
_BONEMATCHER["cheek.B.R.001"]["tail"] = 263

_BONEMATCHER["cheek.T.L"] = dict()
_BONEMATCHER["cheek.T.L"]["head"] = 7032
_BONEMATCHER["cheek.T.L"]["tail"] = 11748
_BONEMATCHER["cheek.T.L.001"] = dict()
_BONEMATCHER["cheek.T.L.001"]["head"] = 11748
_BONEMATCHER["cheek.T.L.001"]["tail"] = 11715

_BONEMATCHER["cheek.B.L"] = dict()
_BONEMATCHER["cheek.B.L"]["head"] = 7185
_BONEMATCHER["cheek.B.L"]["tail"] = 11767
_BONEMATCHER["cheek.B.L.001"] = dict()
_BONEMATCHER["cheek.B.L.001"]["head"] = 11767
_BONEMATCHER["cheek.B.L.001"]["tail"] = 7032

# Nose

_BONEMATCHER["nose"] = dict()
_BONEMATCHER["nose"]["head"] = 132
_BONEMATCHER["nose"]["tail"] = 164
_BONEMATCHER["nose.001"] = dict()
_BONEMATCHER["nose.001"]["head"] = 164
_BONEMATCHER["nose.001"]["tail"] = 297
_BONEMATCHER["nose.002"] = dict()
_BONEMATCHER["nose.002"]["head"] = 297
_BONEMATCHER["nose.002"]["tail"] = 312
_BONEMATCHER["nose.003"] = dict()
_BONEMATCHER["nose.003"]["head"] = 312
_BONEMATCHER["nose.003"]["tail"] = 343
_BONEMATCHER["nose.004"] = dict()
_BONEMATCHER["nose.004"]["head"] = 343
_BONEMATCHER["nose.004"]["tail"] = 467

_BONEMATCHER["nose.R"] = dict()
_BONEMATCHER["nose.R"]["head"] = 5100
_BONEMATCHER["nose.R"]["tail"] = 337
_BONEMATCHER["nose.R.001"] = dict()
_BONEMATCHER["nose.R.001"]["head"] = 337
_BONEMATCHER["nose.R.001"]["tail"] = 297

_BONEMATCHER["nose.L"] = dict()
_BONEMATCHER["nose.L"]["head"] = 11715
_BONEMATCHER["nose.L"]["tail"] = 7099
_BONEMATCHER["nose.L.001"] = dict()
_BONEMATCHER["nose.L.001"]["head"] = 7099
_BONEMATCHER["nose.L.001"]["tail"] = 297

# Chin

_BONEMATCHER["chin"] = dict()
_BONEMATCHER["chin"]["head"] = 5296
_BONEMATCHER["chin"]["tail"] = 5162
_BONEMATCHER["chin.001"] = dict()
_BONEMATCHER["chin.001"]["head"] = 5162
_BONEMATCHER["chin.001"]["tail"] = 724 

_BONEMATCHER["chin.R"] = dict()
_BONEMATCHER["chin.R"]["head"] = 5222
_BONEMATCHER["chin.R"]["tail"] = 425
_BONEMATCHER["chin.L"] = dict()
_BONEMATCHER["chin.L"]["head"] = 11832
_BONEMATCHER["chin.L"]["tail"] = 7185

# Jaw / temple

_BONEMATCHER["jaw"] = dict()
_BONEMATCHER["jaw"]["head"] = 783
_BONEMATCHER["jaw"]["tail"] = 724

_BONEMATCHER["temple.R"] = dict()
_BONEMATCHER["temple.R"]["head"] = 5562
_BONEMATCHER["temple.R"]["tail"] = 867
_BONEMATCHER["jaw.R"] = dict()
_BONEMATCHER["jaw.R"]["head"] = 867
_BONEMATCHER["jaw.R"]["tail"] = 739
_BONEMATCHER["jaw.R.001"] = dict()
_BONEMATCHER["jaw.R.001"]["head"] = 739
_BONEMATCHER["jaw.R.001"]["tail"] = 5222

_BONEMATCHER["temple.L"] = dict()
_BONEMATCHER["temple.L"]["head"] = 12159
_BONEMATCHER["temple.L"]["tail"] = 7572
_BONEMATCHER["jaw.L"] = dict()
_BONEMATCHER["jaw.L"]["head"] = 7572
_BONEMATCHER["jaw.L"]["tail"] = 7459
_BONEMATCHER["jaw.L.001"] = dict()
_BONEMATCHER["jaw.L.001"]["head"] = 7459
_BONEMATCHER["jaw.L.001"]["tail"] = 11832

# Forehead

_BONEMATCHER["forehead.R"] = dict()
_BONEMATCHER["forehead.R"]["head"] = 245
_BONEMATCHER["forehead.R"]["tail"] = 208
_BONEMATCHER["forehead.R.001"] = dict()
_BONEMATCHER["forehead.R.001"]["head"] = 240
_BONEMATCHER["forehead.R.001"]["tail"] = 206
_BONEMATCHER["forehead.R.002"] = dict()
_BONEMATCHER["forehead.R.002"]["head"] = 248
_BONEMATCHER["forehead.R.002"]["tail"] = 254

_BONEMATCHER["forehead.L"] = dict()
_BONEMATCHER["forehead.L"]["head"] = 7015
_BONEMATCHER["forehead.L"]["tail"] = 6983
_BONEMATCHER["forehead.L.001"] = dict()
_BONEMATCHER["forehead.L.001"]["head"] = 7011
_BONEMATCHER["forehead.L.001"]["tail"] = 6981
_BONEMATCHER["forehead.L.002"] = dict()
_BONEMATCHER["forehead.L.002"]["head"] = 7018
_BONEMATCHER["forehead.L.002"]["tail"] = 7023

# Eyelids

_BONEMATCHER["lid.T.R"] = dict()
_BONEMATCHER["lid.T.R"]["head"] = 68
_BONEMATCHER["lid.T.R"]["tail"] = 58
_BONEMATCHER["lid.T.R.001"] = dict()
_BONEMATCHER["lid.T.R.001"]["head"] = 58 
_BONEMATCHER["lid.T.R.001"]["tail"] = 3
_BONEMATCHER["lid.T.R.002"] = dict()
_BONEMATCHER["lid.T.R.002"]["head"] = 3
_BONEMATCHER["lid.T.R.002"]["tail"] = 10
_BONEMATCHER["lid.T.R.003"] = dict()
_BONEMATCHER["lid.T.R.003"]["head"] = 10
_BONEMATCHER["lid.T.R.003"]["tail"] = 85

_BONEMATCHER["lid.B.R"] = dict()
_BONEMATCHER["lid.B.R"]["head"] = 85
_BONEMATCHER["lid.B.R"]["tail"] = 34
_BONEMATCHER["lid.B.R.001"] = dict()
_BONEMATCHER["lid.B.R.001"]["head"] = 34 
_BONEMATCHER["lid.B.R.001"]["tail"] = 43
_BONEMATCHER["lid.B.R.002"] = dict()
_BONEMATCHER["lid.B.R.002"]["head"] = 43
_BONEMATCHER["lid.B.R.002"]["tail"] = 49
_BONEMATCHER["lid.B.R.003"] = dict()
_BONEMATCHER["lid.B.R.003"]["head"] = 49
_BONEMATCHER["lid.B.R.003"]["tail"] = 68

_BONEMATCHER["lid.T.L"] = dict()
_BONEMATCHER["lid.T.L"]["head"] = 6852
_BONEMATCHER["lid.T.L"]["tail"] = 6842
_BONEMATCHER["lid.T.L.001"] = dict()
_BONEMATCHER["lid.T.L.001"]["head"] = 6842
_BONEMATCHER["lid.T.L.001"]["tail"] = 6787
_BONEMATCHER["lid.T.L.002"] = dict()
_BONEMATCHER["lid.T.L.002"]["head"] = 6787
_BONEMATCHER["lid.T.L.002"]["tail"] = 6794
_BONEMATCHER["lid.T.L.003"] = dict()
_BONEMATCHER["lid.T.L.003"]["head"] = 6794
_BONEMATCHER["lid.T.L.003"]["tail"] = 6869

_BONEMATCHER["lid.B.L"] = dict()
_BONEMATCHER["lid.B.L"]["head"] = 6869
_BONEMATCHER["lid.B.L"]["tail"] = 6818
_BONEMATCHER["lid.B.L.001"] = dict()
_BONEMATCHER["lid.B.L.001"]["head"] = 6818
_BONEMATCHER["lid.B.L.001"]["tail"] = 6827
_BONEMATCHER["lid.B.L.002"] = dict()
_BONEMATCHER["lid.B.L.002"]["head"] = 6827
_BONEMATCHER["lid.B.L.002"]["tail"] = 6833
_BONEMATCHER["lid.B.L.003"] = dict()
_BONEMATCHER["lid.B.L.003"]["head"] = 6833
_BONEMATCHER["lid.B.L.003"]["tail"] = 6852

# Teeth

_BONEMATCHER["teeth.B"] = dict()
_BONEMATCHER["teeth.B"]["head"] = 15012
_BONEMATCHER["teeth.B"]["tail"] = "15044 | 15009"

_BONEMATCHER["teeth.T"] = dict()
_BONEMATCHER["teeth.T"]["head"] = 15079
_BONEMATCHER["teeth.T"]["tail"] = "15081 | 15114"

# Tongue

_BONEMATCHER["tongue"] = dict()
_BONEMATCHER["tongue"]["head"] = "joint-tongue-4"
_BONEMATCHER["tongue"]["tail"] = "joint-tongue-3"

_BONEMATCHER["tongue.001"] = dict()
_BONEMATCHER["tongue.001"]["head"] = "joint-tongue-3"
_BONEMATCHER["tongue.001"]["tail"] = "joint-tongue-2"

_BONEMATCHER["tongue.002"] = dict()
_BONEMATCHER["tongue.002"]["head"] = "joint-tongue-2"
_BONEMATCHER["tongue.002"]["tail"] = "joint-tongue-1"


for side in ['l', 'r']:
    sideUp = side.upper()    
    for boneNameSided in _SIDEDMATCHES.keys():
        boneName = str(boneNameSided).replace("#", sideUp)
        head = str(_SIDEDMATCHES[boneNameSided]["head"]).replace("#", side)
        tail = str(_SIDEDMATCHES[boneNameSided]["tail"]).replace("#", side)    
        _BONEMATCHER[boneName] = dict()
        _BONEMATCHER[boneName]["head"] = head
        _BONEMATCHER[boneName]["tail"] = tail

class RigifyUtils:
    
    def __init__(self, obj):
        self._vgNameToIndex = dict()
        self._vgIndexToName = dict()   
        self._vertCoords = dict()     
        self._vgVerts = dict();
        self._vgMeans = dict();
        
        self._obj = obj
        self._buildJointGroupRefs()
        if self.hasDetailedHelpers():
            self._buildVertIndexRefs()
        
    def _buildJointGroupRefs(self):            
        for vg in self._obj.vertex_groups:
            if "joint" in vg.name:        
                self._vgNameToIndex[vg.name] = vg.index
                self._vgIndexToName[vg.index] = vg.name

    def _buildVertIndexRefs(self):  
        for vg in self._obj.vertex_groups:
            if "joint" in vg.name:        
                self._vgVerts[vg.index] = []
                self._vgMeans[vg.name] = None
                
        for v in self._obj.data.vertices:
            self._vertCoords[v.index] = v.co
            for vg in v.groups:
                if (vg.group) in self._vgVerts:
                    self._vgVerts[vg.group].append(v.co)

        for idx in self._vgVerts.keys():
            name = self._vgIndexToName[idx]
            x = 0
            y = 0
            z = 0
            for co in self._vgVerts[idx]:
                x = x + co[0]
                y = y + co[1]
                z = z + co[2]
            x = x / len(self._vgVerts[idx])
            y = y / len(self._vgVerts[idx])
            z = z / len(self._vgVerts[idx])    
            self._vgMeans[name] = [x,y,z]
                              
    def hasDetailedHelpers(self):        
        return "joint-r-knee" in self._vgNameToIndex.keys()
    
    def _average(self, arrayOfArrays):
        count = len(arrayOfArrays)
        size = len(arrayOfArrays[0])
        result = []
        for i in range(size):
            result.append(0.0)
        for n in range(count):
            for i in range(size):
                result[i] = result[i] + arrayOfArrays[n][i]
        for i in range(size):
            result[i] = result[i] / count            
        return result
        
            
    def _getPositionFromMatch(self, boneName, part): 
        match = _BONEMATCHER[boneName]
        matchSub = match[part]        
        if str(matchSub).isnumeric():
            position = self._vertCoords[int(matchSub)]
        else:
            if "|" in matchSub:
                (left, right) = str(matchSub).split("|", 2)
                left = str(left).strip()
                right = str(right).strip()
                if str(left).isnumeric() and str(right).isnumeric():
                    leftCo = self._vertCoords[int(left)]
                    rightCo = self._vertCoords[int(right)]
                    position = self._average([leftCo, rightCo])
                else:
                    position = self._average([self._vgMeans[left], self._vgMeans[right]])        
            else:                    
                position = self._vgMeans[matchSub]
        return position
    
    def _createRig(self):
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()
        self._rig = bpy.context.object
        print("RIG: " + str(self._rig))
        
    def _moveBonePositions(self):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in self._rig.data.edit_bones:
            if bone.name in _BONEMATCHER:                                    
                headPosition = self._getPositionFromMatch(bone.name, "head")
                tailPosition = self._getPositionFromMatch(bone.name, "tail")
                for i in [0,1,2]:            
                    bone.head[i] = headPosition[i]
                    bone.tail[i] = tailPosition[i]
        bpy.ops.object.mode_set(mode='OBJECT')    
        
    def createMetaRig(self):
        self._createRig()
        self._moveBonePositions()
        pprint(_BONEMATCHER)
        
    def generateFinalRig(self, deleteMetaRig=True):
        bpy.ops.pose.rigify_generate()
        self._finalRig = bpy.context.object
        if deleteMetaRig:
            objRef = bpy.data.objects[self._rig.name]
            bpy.data.objects.remove(objRef, do_unlink=True)
            
    
    def removeHelpersAndCubes(self):
        
        helperIdx = None
        cubeIdx = None
        
        for vg in self._obj.vertex_groups:
            if vg.name.lower() == "jointcubes":
                cubeIdx = vg.index
            if vg.name.lower() == "helpergeometry":
                helperIdx = vg.index
        
        print("jointcubes " + str(cubeIdx))
        print("helpers " + str(helperIdx))
                
        bpy.context.view_layer.objects.active = self._obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for vert in self._obj.data.vertices:            
            print("\n")
            print(vert.index)
            for group in vert.groups:                
                if int(group.group) == int(helperIdx) or int(group.group) == int(cubeIdx):            
                    vert.select = True
            
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
                    
    def parentWithWeights(self):
        self._obj.select_set(True)
        self._finalRig.select_set(True)
        bpy.context.view_layer.objects.active = self._finalRig
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        self._finalRig.show_in_front = True
        