import wx, os, sys, os.path, random
import wx.xrc as xrc
from Tribler.vwxGUI.GuiUtility import GUIUtility
from traceback import print_exc
from Tribler.utilities import *
from Tribler.TrackerChecking.ManualChecking import SingleManualChecking
import cStringIO

DEFAULT_THUMB = wx.Bitmap(os.path.join('Tribler', 'vwxGUI', 'images', 'thumbField.png'))
DETAILS_MODES = ['filesMode', 'personsMode', 'profileMode', 'friendsMode', 'subscriptionMode', 'messageMode']
DEBUG = True

ISFRIEND_BITMAP = wx.Bitmap(os.path.join('Tribler', 'vwxGUI', 'images', 'isfriend.png'))

class standardDetails(wx.Panel):
    """
    Wrappers around details xrc panels
    """
    def __init__(self, *args):
        if len(args) == 0:
            pre = wx.PrePanel()
            # the Create step is done by XRC.
            self.PostCreate(pre)
            self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        else:
            wx.Panel.__init__(self, *args)
            self._PostInit()
        
    def OnCreate(self, event):
        self.Unbind(wx.EVT_WINDOW_CREATE)
        wx.CallAfter(self._PostInit)
        event.Skip()
        return True
    
    def _PostInit(self):
        # Do all init here
        self.guiUtility = GUIUtility.getInstance()
        self.utility = self.guiUtility.utility
        self.mode = None
        self.item = None
        self.data = {}
        for mode in DETAILS_MODES+['status']:
            self.data[mode] = {}
        self.currentPanel = None
        self.addComponents()
        #self.Refresh()
        self.modeElements = {'filesMode': ['titleField', 'popularityField1', 'popularityField2', 'creationdateField', 
                                            'descriptionField', 'sizeField', 'thumbField', 'up', 'down', 'refresh', 
                                            'download', 'files_detailsTab', 'info_detailsTab', 'TasteHeart', 'details',],
                             'personsMode': ['TasteHeart', 'recommendationField','addAsFriend', 'commonFilesField', 'alsoDownloadedField']
                             }
        self.tabElements = {'filesTab_files': ['includedFilesField', 'download', 'includedFiles']}

        self.guiUtility.initStandardDetails(self)

        
    def addComponents(self):
        self.SetBackgroundColour(wx.Colour(102,102,102))
        self.hSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.hSizer)
        self.SetAutoLayout(1)
        self.Layout()
        
    def setMode(self, mode, item = None):
        if self.mode != mode:
            self.mode = mode
            self.refreshMode()
        if item:
            self.setData(item)
    
    def getMode(self):
        return self.mode
            
    def refreshMode(self):
        # load xrc
        self.oldpanel = self.currentPanel
        #self.Show(False)
        
        self.currentPanel = self.loadPanel()
        assert self.currentPanel, "Panel could not be loaded"
        self.currentPanel.Layout()
        self.currentPanel.SetAutoLayout(1)
        #self.currentPanel.Enable(True)
        self.currentPanel.Show(True)
        
        if self.oldpanel:
            self.hSizer.Detach(self.oldpanel)
            self.oldpanel.Hide()
            #self.oldpanel.Disable()
        
        self.hSizer.Insert(0, self.currentPanel, 0, wx.ALL|wx.EXPAND, 0)
        
            
            
        self.hSizer.Layout()
        self.currentPanel.Refresh()
        #self.Show(True)
        
        
    def refreshStatusPanel(self, show):
        if show:
            statusPanel = self.data['status'].get('panel')
            if not statusPanel:
                statusPanel = self.loadStatusPanel()
                self.data['status']['panel'] = statusPanel
            #statusPanel.Enable()
            statusPanel.Show()
            self.hSizer.Insert(1, statusPanel, 0, wx.TOP|wx.EXPAND, 6)
            self.hSizer.Layout()
        else:
            # Remove statusPanel if necessary
            if self.data['status'].get('panel'):
                statusPanel = self.data['status']['panel']
                try:
                    self.hSizer.Detach(statusPanel)
                    statusPanel.Hide()
                    #statusPanel.Disable()
                except:
                    print_exc()
        
    def setListAspect2OneColumn(self, list_name):
        ofList = self.getGuiObj(list_name)
        ofList.ClearAll()
        ofList.SetSingleStyle(wx.NO_BORDER)
        ofList.SetSingleStyle(wx.LC_REPORT)
        ofList.SetSingleStyle(wx.LC_NO_HEADER)
        ofList.SetSingleStyle(wx.LC_SINGLE_SEL)
#                ofList.SetWindowStyleFlag(wx.LC_REPORT|wx.NO_BORDER|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL) #it doesn't work
        ofList.InsertColumn(0, "Torrent")
#        ofList.SetColumnWidth(0,wx.LIST_AUTOSIZE)
        
    def loadPanel(self):
        currentPanel = self.data[self.mode].get('panel',None)
        modeString = self.mode[:-4]
        if not currentPanel:
            xrcResource = os.path.join('Tribler','vwxGUI', modeString+'Details.xrc')
            panelName = modeString+'Details'
            currentPanel = self.loadXRCPanel(xrcResource, panelName)
            
            # Save paneldata in self.data
            self.data[self.mode]['panel'] = currentPanel
            #titlePanel = xrc.XRCCTRL(currentPanel, 'titlePanel')
            
            for element in self.modeElements[self.mode]:
                xrcElement = xrc.XRCCTRL(currentPanel, element)
                if not xrcElement:
                    print 'standardDetails: Error: Could not identify xrc element: %s for mode %s' % (element, self.mode)
                self.data[self.mode][element] = xrcElement
            
            # do extra init
            if modeString == 'files':
                print 'extra files init'
                self.getGuiObj('up').setBackground(wx.WHITE)
                self.getGuiObj('down').setBackground(wx.WHITE)
                self.getGuiObj('refresh').setBackground(wx.WHITE)
                self.getGuiObj('TasteHeart').setBackground(wx.WHITE)
                self.getGuiObj('info_detailsTab').setSelected(True)
            elif modeString == 'persons':
                self.getGuiObj('TasteHeart').setBackground(wx.WHITE)
                #get the list in the right mode for viewing
                self.setListAspect2OneColumn("alsoDownloadedField")
                self.setListAspect2OneColumn("commonFilesField")
                
        return currentPanel
    
    def loadStatusPanel(self):
        return self.loadXRCPanel(os.path.join('Tribler','vwxGUI', 'statusDownloads.xrc'), 'statusDownloads')
    
    def loadXRCPanel(self, filename, panelName, parent=None):
        try:
            currentPanel = None
            res = xrc.XmlResource(filename)
            # create panel
            if parent:
                currentPanel = res.LoadPanel(parent, panelName)
            else:
                currentPanel = res.LoadPanel(self, panelName)
            if not currentPanel:
                raise Exception()
            return currentPanel
        except:
            print 'Error: Could not load panel from XRC-file %s' % filename
            print 'Tried panel: %s=%s' % (panelName, currentPanel)
            print_exc()
            return None
            
     
    def getData(self):
        return self.item
    
    def getIdentifier(self):
        if not self.item:
            return None
        try:
            if self.mode == 'filesMode':
                return self.item['infohash']
            elif self.mode == 'personsMode':
                return self.item['permid']
        except:
            print 'standardDetails: Error in getIdentifier, item=%s' % self.item
        
    def setData(self, item):
        self.item = item
        if self.mode == 'filesMode':
            torrent = item
            if not torrent:
                return
            
            titleField = self.getGuiObj('titleField')
            titleField.SetLabel(torrent.get('content_name'))
            titleField.Wrap(-1)
            
            self.setTorrentThumb(torrent, self.getGuiObj('thumbField'))        
            
            if self.getGuiObj('info_detailsTab').isSelected():
                # The info tab is selected, show normal torrent info
                if torrent.has_key('description'):
                    descriptionField = self.getGuiObj('descriptionField')
                    descriptionField.SetLabel(torrent.get('Description'))
                    descriptionField.Wrap(-1)        
    
                if torrent.has_key('length'):
                    sizeField = self.getGuiObj('sizeField')
                    sizeField.SetLabel(self.utility.size_format(torrent['length']))
                
                if torrent.get('info', {}).get('creation date'):
                    creationField = self.getGuiObj('creationdateField')
                    creationField.SetLabel(friendly_time(torrent['info']['creation date']))\
                    
                if torrent.has_key('seeder'):
                    seeders = torrent['seeder']
                    seedersField = self.getGuiObj('popularityField1')
                    leechersField = self.getGuiObj('popularityField2')
                    
                    if seeders > -1:
                        seedersField.SetLabel('%d' % seeders)
                        leechersField.SetLabel('%d' % torrent['leecher'])
                    else:
                        seedersField.SetLabel('?')
                        leechersField.SetLabel('?')
            
            elif self.getGuiObj('files_detailsTab').isSelected():
                filesList = self.getGuiObj('includedFiles', tab = 'filesTab_files')
                
                filesList.setData(torrent)
                
            else:
                print 'standardDetails: error: unknown tab selected'
            
                        
        elif self.mode in ['personsMode', 'friendsMode']:
            #recomm = random.randint(0,4)
            rank = self.guiUtility.peer_manager.getRank(item['permid'])
            #because of the fact that hearts are coded so that lower index means higher ranking, then:
            if rank > 0 and rank <= 5:
                recomm = 0
            elif rank > 5 and rank <= 10:
                recomm = 1
            elif rank > 10 and rank <= 15:
                recomm = 2
            elif rank > 15 and rank <= 20:
                recomm = 3
            else:
                recomm = 4
            if rank != -1:
                self.getGuiObj('recommendationField').SetLabel("%d" % rank + " of 20")
            else:
                self.getGuiObj('recommendationField').SetLabel("")
            if recomm != -1:
                self.getGuiObj('TasteHeart').setHeartIndex(recomm)
            else:
                self.getGuiObj('TasteHeart').setHeartIndex(0)
            
            if item['friend']:
                self.getGuiObj('addAsFriend').Enable(False)
                self.getGuiObj('addAsFriend').switchTo(ISFRIEND_BITMAP)
            else:
                self.getGuiObj('addAsFriend').switchBack()
                self.getGuiObj('addAsFriend').Enable(True)
                
            self.fillTorrentLists()
            
        elif self.mode == 'libraryMode':
            pass
        elif self.mode == 'subscriptionMode':
            pass

        self.currentPanel.Refresh()
        
    def getGuiObj(self, obj_name, tab=None):
        """handy function to retreive an object based on it's name for the current mode"""
        if tab:
            obj_name = tab+'_'+obj_name
        return self.data[self.mode].get(obj_name)
        
    def fillTorrentLists(self):
        ofList = self.getGuiObj("alsoDownloadedField")
#        ofList.SetWindowStyleFlag(wx.LC_LIST)
        cfList = self.getGuiObj("commonFilesField")
#        cfList.SetWindowStyleFlag(wx.LC_LIST)
        try:
            if self.mode != "personsMode" or self.item==None or self.item['permid']==None:
                return
            permid = self.item['permid']
            hash_list = self.guiUtility.peer_manager.getPeerHistFiles(permid)
            torrents_info = self.guiUtility.data_manager.getTorrents(hash_list)
#            # get my download history
#            hist_torr = self.parent.mydb.getPrefList()
#            #print hist_torr
#            files = self.parent.prefdb.getPrefList(self.data['permid'])
#            #live_files = self.torrent_db.getLiveTorrents(files)
#            #get informations about each torrent file based on it's hash
#            torrents_info = self.parent.tordb.getTorrents(files)
#            for torrent in torrents_info[:]:
#                if (not 'info' in torrent) or (len(torrent['info']) == 0) or (not 'name' in torrent['info']):
#                    torrents_info.remove(torrent)
#            #sort torrents based on status: { downloading (green), seeding (yellow),} good (blue), unknown(black), dead (red); 
#            torrents_info.sort(self.status_sort)
#            torrents_info = filter( lambda torrent: not torrent['status'] == 'dead', torrents_info)
            #tempdata[i]['torrents_list'] = torrents_info
            ofList.DeleteAllItems()
            cfList.DeleteAllItems()
            for f in torrents_info:
                #print f
                the_list = None
                if f.get('myDownloadHistory', False):
                    the_list = cfList
                else:
                    the_list = ofList
                index = the_list.InsertStringItem(sys.maxint, f['info']['name'])
                color = "black"
                if f['status'] == 'good':
                    color = "blue"
                elif f['status'] == 'unknown':
                    color = "black"
                elif f['status'] == 'dead':
                    color = "red"
                the_list.SetItemTextColour(index, color)
                #self.ofList.SetStringItem(index, 1, f[1])
            if cfList.GetItemCount() == 0:
                index = cfList.InsertStringItem(sys.maxint, "No common files with this person.")
                font = cfList.GetItemFont(index)
                font.SetStyle(wx.FONTSTYLE_ITALIC)
                cfList.SetItemFont(index, font)
                cfList.SetItemTextColour(index, "#f0c930")
            if ofList.GetItemCount() == 0:
                index = ofList.InsertStringItem(sys.maxint, "No files advertised by this person.")
                font = ofList.GetItemFont(index)
                font.SetStyle(wx.FONTSTYLE_ITALIC)
                ofList.SetItemFont(index, font)
                ofList.SetItemTextColour(index, "#f0c930")
#            self.onListResize(None) 
        except Exception, e:
            print_exc(e)
            ofList.DeleteAllItems()
            cfList.DeleteAllItems()
            index = ofList.InsertStringItem(sys.maxint, "Error getting files list")
            ofList.SetItemTextColour(index, "dark red")
        try:
            ofList.onListResize() #SetColumnWidth(0,wx.LIST_AUTOSIZE)
            cfList.onListResize() #SetColumnWidth(0,wx.LIST_AUTOSIZE)
        except:
            if DEBUG:
                print "could not resize lists in person detail panel"
        
    def tabClicked(self, name):
        print 'Tabclicked: %s' % name
        
        # currently, only tabs in filesDetailspanel work
        if self.mode != 'filesMode':
            print 'standardDetails: Tabs for !filesDetails not yet implement'
            return
        
        tabFiles = self.getGuiObj('files_detailsTab')
        tabInfo = self.getGuiObj('info_detailsTab')
        
        if name == 'files_detailsTab' and not tabFiles.isSelected():
            tabFiles.setSelected(True)
            tabInfo.setSelected(False)
            infoPanel = self.getGuiObj('details')
            sizer = infoPanel.GetContainingSizer()
            filesPanel = self.getAlternativeTabPanel('filesTab_files')
            self.swapPanel(sizer, 3, infoPanel, filesPanel)
            
        elif name == 'info_detailsTab' and not tabInfo.isSelected():
            tabFiles.setSelected(False)
            tabInfo.setSelected(True)
            
            filesPanel = self.getGuiObj('filesTab_files')
            sizer = filesPanel.GetContainingSizer()
            infoPanel = self.getGuiObj('details')
            self.swapPanel(sizer, 3, filesPanel, infoPanel)
            
        else:
            print 'standardDetails: Unknown tabs'
            return
        
        self.setData(self.item)
        
            
    def swapPanel(self, sizer, index, oldpanel, newpanel):
        # remove info tab panel
        sizer.Detach(oldpanel)
        oldpanel.Hide()
        # add files tab panel
        sizer.Insert(index, newpanel, 1, wx.EXPAND, 3)
        if not newpanel.IsShown():
            newpanel.Show()
        sizer.Layout()
        newpanel.GetParent().Refresh()
        
        
    def getAlternativeTabPanel(self, name):
        "Load a tabPanel that was not loaded as default"
        panel = self.getGuiObj(name)
        if panel:
            return panel
        else:
            # generate new panel
            xrcResource = os.path.join('Tribler','vwxGUI', name+'.xrc')
            panelName = name
            panel = self.loadXRCPanel(xrcResource, panelName, parent=self.currentPanel)
            
            for element in self.tabElements[name]:
                xrcElement = xrc.XRCCTRL(panel, element)
                if not xrcElement:
                    print 'standardDetails: Error: Could not identify xrc element: %s for mode %s' % (element, self.mode)
                self.data[self.mode][name+'_'+element] = xrcElement
                            
            self.data[self.mode][name] = panel
                
            return panel
        
    def mouseAction(self, event):
        print 'mouseAction'
        
        obj = event.GetEventObject()
        print obj
        
        if not self.data:
            return
        if obj == self.downloadButton:
            self.download(self.data)
        elif obj == self.refreshButton: 
            #and self.refreshButton.isEnabled():
            print "refresh seeders and leechers"
            #self.swarmText.SetLabel(self.utility.lang.get('refreshing')+'...')
            #self.swarmText.Refresh()
            
            self.refresh(self.data)
            
    def refresh(self, torrent):
        if DEBUG:
            print >>sys.stderr,'contentpanel: refresh ' + repr(torrent.get('content_name', 'no_name'))
        check = SingleManualChecking(torrent)
        check.start()
            
#    def isEnabled(self):
#        return self.enabled

    def download(self, torrent):
        src1 = os.path.join(torrent['torrent_dir'], 
                            torrent['torrent_name'])
        src2 = os.path.join(self.utility.getConfigPath(), 'torrent2', torrent['torrent_name'])
        if torrent['content_name']:
            name = torrent['content_name']
        else:
            name = showInfoHash(torrent['infohash'])
        #start_download = self.utility.lang.get('start_downloading')
        #str = name + "?"
        if os.path.isfile(src1):
            src = src1
        else:
            src = src2
            
        if os.path.isfile(src):
            str = self.utility.lang.get('download_start') + u' ' + name + u'?'
            dlg = wx.MessageDialog(self, str, self.utility.lang.get('click_and_download'), 
                                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                ret = self.utility.queue.addtorrents.AddTorrentFromFile(src)
                if ret == 'OK':
                    self.setRecommendedToMyDownloadHistory(torrent)
                    
        else:
        
            # Torrent not found            
            str = self.utility.lang.get('delete_torrent') % name
            dlg = wx.MessageDialog(self, str, self.utility.lang.get('delete_dead_torrent'), 
                                wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                infohash = torrent['infohash']
                self.data_manager.deleteTorrent(infohash, delete_file = True)
            
    def setTorrentThumb(self, torrent, thumbPanel):
        
        if not thumbPanel:
            return 
        
        thumbBitmap = torrent.get('metadata',{}).get('ThumbnailBitmapLarge')
        thumbnailString = torrent.get('metadata', {}).get('Thumbnail')
        
        if thumbBitmap:
            thumbPanel.setBitmap(thumbBitmap)
            
        elif thumbnailString:
            #print 'Found thumbnail: %s' % thumbnailString
            stream = cStringIO.StringIO(thumbnailString)
            img =  wx.ImageFromStream( stream )
            iw, ih = img.GetSize()
            w, h = thumbPanel.GetSize()
            if (iw/float(ih)) > (w/float(h)):
                nw = w
                nh = int(ih * w/float(iw))
            else:
                nh = h
                nw = int(iw * h/float(ih))
            if nw != iw or nh != ih:
                #print 'Rescale from (%d, %d) to (%d, %d)' % (iw, ih, nw, nh)
                img.Rescale(nw, nh, quality = wx.IMAGE_QUALITY_HIGH)
            bmp = wx.BitmapFromImage(img)
             
            thumbPanel.setBitmap(bmp)
            torrent['metadata']['ThumbnailBitmapLarge'] = bmp
        else:
             thumbPanel.setBitmap(DEFAULT_THUMB)
            
class FilesTabPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.guiUtility = GUIUtility.getInstance()
        self.utility = self.guiUtility.utility
        self.addComponents()
        
    def addComponents(self):
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.numFilesField = wx.StaticText(self, -1, self.utility.lang.get('torrent_files') % 0)
        self.vSizer.Add(self.numFilesField, 0, wx.EXPAND|wx.ALL, 10)
        
        self.fileList = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL )
        self.fileList.InsertColumn(0, self.utility.lang.get('file'))
        self.fileList.InsertColumn(1, self.utility.lang.get('size'))
        self.fileList.Bind(wx.EVT_SIZE, self.onListResize)
                
        if sys.platform == 'win32':
            #print 'Using windows code'
            self.vSizer.Add(self.fileList, 1, wx.ALL|wx.EXPAND, 1)
        else:
            #print 'Using unix code'
            BORDER_EXPAND = wx.ALL|wx.GROW
            self.fileListSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.fileListSizer.Add(self.fileList, 1, BORDER_EXPAND, 0)
            self.vSizer.Add(self.fileListSizer, 1, BORDER_EXPAND, 1)
        

        self.SetSizer(self.vSizer);self.SetAutoLayout(1);self.Layout();
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize((-1, 348)) # set same size as default info panel
        self.Refresh()
        
    def setData(self, torrent):
        # Get the file(s)data for this torrent
        
        print 'setData of FilesTabPanel called'
        torrent_dir = torrent.get('torrent_dir')
        torrent_file = torrent.get('torrent_name')
        try:
            
            if not os.path.exists(torrent_dir):
                torrent_dir = os.path.join(self.utility.getConfigPath(), "torrent2")
            
            torrent_filename = os.path.join(torrent_dir, torrent_file)
            
            if not os.path.exists(torrent_filename):
                if DEBUG:    
                    print >>sys.stderr,"contentpanel: Torrent: %s does not exist" % torrent_filename
                return {}
            
            metadata = self.utility.getMetainfo(torrent_filename)
            if not metadata:
                return {}
            info = metadata.get('info')
            if not info:
                return {}
            
            #print metadata.get('comment', 'no comment')
                
                
            filedata = info.get('files')
            if not filedata:
                filelist = [(dunno2unicode(info.get('name')),self.utility.size_format(info.get('length')))]
            else:
                filelist = []
                for f in filedata:
                    filelist.append((dunno2unicode('/'.join(f.get('path'))), self.utility.size_format(f.get('length')) ))
                filelist.sort()
                
            
            # Add the filelist to the fileListComponent
            self.fileList.DeleteAllItems()
            for f in filelist:
                index = self.fileList.InsertStringItem(sys.maxint, f[0])
                self.fileList.SetStringItem(index, 1, f[1])
            self.onListResize(None)
            
            # update number of files
            self.numFilesField.SetLabel(self.utility.lang.get('torrent_files') % len(filelist))
            
        except:
            print 'standardDetails: error getting list of files in torrent'
            print_exc(file=sys.stderr)
            return {}                 
        
    def onListResize(self, event):
        size = self.fileList.GetClientSize()
        if size[0] > 50 and size[1] > 50:
            self.fileList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.fileList.SetColumnWidth(0, self.fileList.GetClientSize()[0]-self.fileList.GetColumnWidth(1)-15)
            self.fileList.ScrollList(-100, 0) # Removes HSCROLLBAR
        if event:
            event.Skip()
