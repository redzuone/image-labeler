from main import show_image
from main import Image, ImageLabeler
import PySimpleGUI as sg
import os
import logging

def main():
    processor = ImageLabeler()
    show_image_flag = rename_file_flag = False
    images = []
    image_index = 0 # index
    sg.theme('DarkAmber')
    layout = [[sg.Button('Process a file')],
                [sg.Button('Process a folder')],
                [sg.Text('Path: ', key='path')],
                [sg.Checkbox('Show image result using matplotlib (single image)', enable_events=True, key='show_image_event')],
                [sg.Checkbox('Rename file instead of copying', enable_events=True, key='rename_file_event')],
                [sg.Checkbox('Manual mode', enable_events=True, key='manual_mode_event')],
                [sg.Text('Status: '), sg.Text('Ready', key='status')],
                [sg.Col([[sg.Text('Results')]], scrollable=True, key='-COL-', s=(1280,720))],]
    window = sg.Window('Image Labeler', layout, size=(1280, 720))
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'show_image_event':
            show_image_flag = window['show_image_event'].get()
        elif event == 'rename_file_event':
            rename_file_flag = window['rename_file_event'].get()
        elif event == 'manual_mode_event':
            manual_mode_flag = window['manual_mode_event'].get()

        elif event == 'Process a file':
            image_path = sg.popup_get_file('Pick file')
            if not image_path:
                continue
            else:
                images.append(Image(image_path))
                window['path'].update(image_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: processor.process_single_file(images[image_index], rename_file_flag), 'single_file_done')
        
        elif event == 'single_file_done':
            image = images[image_index]
            window['status'].update('Done')
            window.extend_layout(window['-COL-'], [[sg.Image(data=image.image_annotated, size=(None, 300))],
                                                   [sg.Text('File: ' + image.image_path)],
                                                   [sg.Text('Text: ' + image.text)],
                                                   [sg.Button('Rename file', key='rename_' + str(image_index))],
                                                   [sg.Text('', key='new_image_path_label' + str(image_index))]])
            image_index += 1
            window.visibility_changed()
            window['-COL-'].contents_changed()
            if show_image_flag == True:
                image_path = window['path'].get()
                #show_image(image_path, result)
        
        elif event.startswith('rename'):
            _, image_index = event.split('_')
            image_index = int(image_index)
            image = images[image_index]
            logging.debug(f'Rename image index {image_index}')
            text = image.text
            image_path = image.image_path
            processor.rename_file(image)
            new_image_path = image.new_image_path
            # check if file exists
            if os.path.exists(new_image_path):
                window['new_image_path_label' + str(image_index)].update('Output: ' + new_image_path)
                # rename and disable button
                window['rename_' + str(image_index)].update('Renamed', disabled=True)
            else:
                window['new_image_path_label' + str(image_index)].update('Error')

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
                                                   [sg.Button('Rename file', key='rename_' + str(image_index))],
                                                   [sg.Text('', key='new_image_path_label' + str(image_index))]])
                image_index += 1
            window.visibility_changed()
            window['-COL-'].contents_changed()

if __name__ == '__main__':
    # rename test files
    folders = ['test/multiple/', 'test/']
    for folder in folders:
        folder_path = folder
        files = os.listdir(folder_path)
        supported_files = ['.jpg', '.png', '.jpeg', '.webp', '.heic']
        for i, file in enumerate(files):
            if file.endswith(tuple(supported_files)):
                # new filename
                if folder_path == 'test/':
                    new_filename = f'test{os.path.splitext(file)[1]}'
                else:
                    new_filename = f'test{i}{os.path.splitext(file)[1]}'
                os.rename(folder_path + file, folder_path + new_filename)
    main()