from main import process_single_file, process_images_in_folder, show_image, rename_file
import PySimpleGUI as sg
import os
import logging

def main():
    show_image_flag = rename_file_flag = False
    img_path = ''
    img_data = []
    img_count = 0
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
            img_path = sg.popup_get_file('Pick file')
            if not img_path:
                continue
            else:
                window['path'].update(img_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: process_single_file(img_path, rename_file_flag), 'single_file_done')
        
        elif event == 'single_file_done':
            text, result = values[event]
            window['status'].update('Done')
            print('new file index ' + str(img_count))
            window.extend_layout(window['-COL-'], [[sg.Image(filename='tmp.png', size=(None, 300))],
                                                   [sg.Text('File: ' + img_path)],
                                                   [sg.Text('Text: ' + text)],
                                                   [sg.Button('Rename file', key='rename_' + str(img_count)), sg.Button('Reject', key='reject')],
                                                   [sg.Text('', key='new_img_path')]])
            img_data.append({ 'img_path': img_path, 'text': text, 'result': result })
            img_count += 1
            window.visibility_changed()
            window['-COL-'].contents_changed()
            if show_image_flag == True:
                img_path = window['path'].get()
                show_image(img_path, result)
        
        elif event.startswith('rename'):
            _, img_index = event.split('_')
            img_index = int(img_index)
            print('rename file at ' + str(img_index))
            img_text = img_data[img_index]['text']
            img_path = img_data[img_index]['img_path']
            # Save the image. call def rename_file(image_path, text):
            # to get img_path, need a storage that pair img_path with text
            # need t
            rename_file(img_path, img_text)
            directory = os.path.dirname(img_path)
            img_text = img_text.replace(' ', '_')
            new_img_filename = img_text + os.path.splitext(img_path)[1]
            new_img_path = os.path.join(directory, new_img_filename)
            print(new_img_path)
            if os.path.exists(new_img_path):
                window['new_img_path'].update('Output: ' + new_img_path)
                # rename and disable button
                window['rename_' + str(img_index)].update(disabled=True)
            else:
                window['new_img_path'].update('Error')


        elif event == 'Process a folder':
            folder_path = sg.popup_get_folder('Pick folder')
            if not folder_path:
                continue
            else:
                window['path'].update(folder_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: process_images_in_folder(folder_path), 'folder_done')
        
        elif event == 'folder_done':
            window['status'].update('Done, files are saved in output folder')
            #text, result = values[event]
            #save_image_box_gui(img_path, result)
            #window.extend_layout(window['-COL-'], [[sg.Image(filename='tmp.png', size=(None, 300)), sg.T(text, size=(300, None))]])
            #window.visibility_changed()
            #window['-COL-'].contents_changed()


if __name__ == '__main__':
    main()