# Image Labeler

Renames pictures based on the text in them using PaddleOCR. 

# Usage
Install [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/quickstart_en.md).    
Command line: Run `main.py` directly or with arguments
```
--file=FILE     Process a single image
--dir=DIRECTORY     Process multiples images in a folder
--copy              Copy file with new filename instead of renaming  
```

GUI: Run `gui_simple.py` 
The program creates copies the image file with its new name by default.

# To-do
- [ ] Object/content recognition (maybe)
- [ ] Add more comments
- [ ] Remove common/unnecessary text from new filename/pick most useful text
- [ ] Clean code

# Libraries used
- PaddleOCR
- PySimpleGUI

# Demo
https://github.com/redzuone/image-labeler/assets/21290781/d6e28d3d-5449-4946-89fe-346662877be8

