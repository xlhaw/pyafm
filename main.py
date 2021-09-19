import os,re,pandas as pd
from analyze import read_afm,get_list,get_profile

from kivy.core.window import Window
Window.size=(360,540)
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast

#TODO print progress and logs
def get_hdi_task(wd):
    bills=get_list(f'{wd}\\Process_Data')
    task={}
    for bill in bills:
        task[bill]=[file for file in os.listdir(bill) if 'HDI_AfterFlatten' in file]
    return task
def hdi_summary(old,new):
    if 'MidMR Max' in old.columns:
        return old
    new['ROWNO']=new.index.str[1:3].astype(int)
    new['SLDNO']=new.index.str[-2:].astype(int)
    new=new.rename(columns={'MidMR \nMax':'MidMR Max'})
    summary=old.merge(new,left_on=['ROWNO','SLDNO'],right_on=['ROWNO','SLDNO'])
    return summary
def hdi_analysis(wd):
    task=get_hdi_task(wd)
    csv_file=get_list(wd,'csv')[0]
    old=pd.read_csv(csv_file)
    old=old.rename(columns={old.columns[0]:''})
    results=[]
    for bill,files in task.items():
        bill=bill.split('\\')[-1]
        img_dir=f'{wd}\\Capture_Image_With_Offset\\{bill}'
        for file in files:
            afm=read_afm(os.path.join(wd,'Process_Data',bill,file))
            sld=re.findall(r'(.\d\d-\d\d)',file)[0]
            df=get_profile(afm,smoothed=False,plot=True,fname=f'{img_dir}\\{sld} Wav')
            df.index=[sld]
            results.append(df)
    new=pd.concat(results)
    summary=hdi_summary(old,new)
    summary.to_csv(csv_file,index=False)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
        exit_manager=self.exit_manager,
        select_path=self.select_path,
        preview=True,
        )
    #def build(self):
    #    return Builder.load_string(KV)
    def file_manager_open(self):
        self.file_manager.show('/') # output manager to the screen
        self.manager_open = True
    def set_item(self, text_item):
        self.screen.ids.field.text = text_item
    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        '''
        self.root.ids.field.text = path
        self.exit_manager()
        toast(path)
    def start_analyze(self):
        hdi_analysis(self.file_manager.current_path)
        toast('Finished!')
    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()
    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

if __name__=='__main__':
    MainApp().run()
