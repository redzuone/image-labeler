from main import show_image, rename_test_files
from main import Image, ImageLabeler
import PySimpleGUI as sg
import os
import logging

def main():
    processor = ImageLabeler()
    show_image_flag = rename_file_flag = False
    images = []
    image_index = 0
    sg.theme('DarkAmber')
    layout = [[sg.Button('Process a file')],
                [sg.Button('Process a folder')],
                [sg.Text('Path: ', key='path')],
                [sg.Checkbox('Show image result using matplotlib (single image)', enable_events=True, key='show_image_event')],
                [sg.Checkbox('Copy mode', enable_events=True, key='copy_mode_event')],
                [sg.Checkbox('Interactive renaming mode', enable_events=True, key='interactive_mode_event')],
                [sg.Text('Status: '), sg.Text('Ready', key='status')],
                [sg.Col([[sg.Text('Results')]], scrollable=True, key='-COL-', s=(1280,720))],]
    window = sg.Window('Image Labeler', layout, size=(1280, 720))
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'show_image_event':
            show_image_flag = window['show_image_event'].get()
        elif event == 'copy_mode_event':
            processor.copy_mode_flag = window['copy_mode_event'].get()
        elif event == 'interactive_mode_event':
            processor.interactive_mode_flag = window['interactive_mode_event'].get()
            processor.copy_mode_flag = False
            if processor.interactive_mode_flag == True:
                window['copy_mode_event'].update(False, disabled=True)
            else:
                window['copy_mode_event'].update(False, disabled=False)

        elif event == 'Process a file':
            image_path = sg.popup_get_file('Pick file')
            if not image_path:
                continue
            else:
                logging.debug(f'Picked image {image_path}')
                images.append(Image(image_path))
                window['path'].update(image_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: processor.process_single_file(images[image_index]), 'single_file_done')
        
        elif event == 'single_file_done':
            image = images[image_index]
            window['status'].update('Done')
            window.extend_layout(window['-COL-'], [[sg.Image(data=image.image_annotated, size=(None, 300))],
                                                   [sg.Text('File: ' + image.image_path)],
                                                   [sg.Text('Text: ' + image.text)],
                                                   [sg.Button('Rename file', key='rename_' + str(image_index), visible=False)],
                                                   [sg.Text('', key='new_image_path_label' + str(image_index))]])
            if processor.interactive_mode_flag == True:
                window['rename_' + str(image_index)].update(visible=True)
            image_index += 1
            window.visibility_changed()
            window['-COL-'].contents_changed()
            if show_image_flag == True:
                show_image(image)
        
        elif event.startswith('rename'):
            _, image_index_rename = event.split('_')
            image_index_rename = int(image_index_rename)
            image = images[image_index_rename]
            logging.debug(f'Rename image index {image_index_rename}')
            processor.rename_file(image)
            new_image_path = image.new_image_path
            # check if file exists
            if os.path.exists(new_image_path):
                window['new_image_path_label' + str(image_index_rename)].update('Output: ' + new_image_path)
                # rename and disable button
                window['rename_' + str(image_index_rename)].update('Renamed', disabled=True)
            else:
                window['new_image_path_label' + str(image_index_rename)].update('Error')

        elif event == 'Process a folder':
            folder_path = sg.popup_get_folder('Pick folder')
            if not folder_path:
                continue
            else:
                window['path'].update(folder_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: processor.process_images_in_folder(folder_path), 'folder_done')
        
        elif event == 'folder_done':
            window['status'].update('Done, files are saved in output folder')
            processed_images = values[event]
            for image in processed_images:
                images.append(image)
                window.extend_layout(window['-COL-'], [[sg.Image(data=image.image_annotated, size=(None, 300))],
                                                   [sg.Text('File: ' + image.image_path)],
                                                   [sg.Text('Text: ' + image.text)],
                                                   [sg.Button('Rename file', key='rename_' + str(image_index), visible=False)],
                                                   [sg.Text('', key='new_image_path_label' + str(image_index))]])
                image_index += 1
            if processor.interactive_mode_flag == True:
                for i in range(len(images)):
                    window['rename_' + str(i)].update(visible=True)
            window.visibility_changed()
            window['-COL-'].contents_changed()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logging.getLogger('PIL').setLevel(logging.WARNING)
    rename_test_files()
    main()