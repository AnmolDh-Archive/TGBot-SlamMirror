from bot import aria2, download_dict_lock, STOP_DUPLICATE_MIRROR, TORRENT_DIRECT_LIMIT
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.ext_utils.bot_utils import *
from .download_helper import DownloadHelper
from bot.helper.mirror_utils.status_utils.aria_download_status import AriaDownloadStatus
from bot.helper.telegram_helper.message_utils import *
import threading
from aria2p import API
from time import sleep


class AriaDownloadHelper(DownloadHelper):

    def __init__(self):
        super().__init__()

    @new_thread
    def __onDownloadStarted(self, api, gid):
        if STOP_DUPLICATE_MIRROR or TORRENT_DIRECT_LIMIT is not None:
            sleep(1)
            dl = getDownloadByGid(gid)
            download = api.get_download(gid)
            
            if STOP_DUPLICATE_MIRROR:
                LOGGER.info(f"Checking File/Folder if already in Drive...")
                self.name = download.name
                sname = download.name
                if self.listener.isTar:
                    sname = sname + ".tar"
                if self.listener.extract:
                    smsg = None
                else:
                    gdrive = GoogleDriveHelper(None)
                    smsg, button = gdrive.drive_list(sname)
                if smsg:
                    dl.getListener().onDownloadError(f'File/Folder is already available in Drive.\n\n')
                    sendMarkup("Here are the search results:", dl.getListener().bot, dl.getListener().update, button)
                    aria2.remove([download])
                    return

            if TORRENT_DIRECT_LIMIT is not None:
                LOGGER.info(f"Checking File/Folder Size...")
                with download_dict_lock:
                    for down in list(download_dict.values()):
                        sleep(1)
                        size = down.size_raw()
                limit = TORRENT_DIRECT_LIMIT
                limit = limit.split(' ', maxsplit=1)
                limitint = int(limit[0])
                if 'GB' in limit or 'gb' in limit:
                    if size > limitint * 1024**3:
                        dl.getListener().onDownloadError(f'Torrent/Direct limit is {TORRENT_DIRECT_LIMIT}.\nYour File/Folder size is {get_readable_file_size(size)}')
                        aria2.remove([download])
                        return
                elif 'TB' in limit or 'tb' in limit:
                    if size > limitint * 1024**4:
                        dl.getListener().onDownloadError(f'Torrent/Direct limit is {TORRENT_DIRECT_LIMIT}.\nYour File/Folder size is {get_readable_file_size(size)}')
                        aria2.remove([download])
                        return
        update_all_messages()

    def __onDownloadComplete(self, api: API, gid):
        LOGGER.info(f"onDownloadComplete: {gid}")
        dl = getDownloadByGid(gid)
        download = api.get_download(gid)
        if download.followed_by_ids:
            new_gid = download.followed_by_ids[0]
            new_download = api.get_download(new_gid)
            with download_dict_lock:
                download_dict[dl.uid()] = AriaDownloadStatus(new_gid, dl.getListener())
                if new_download.is_torrent:
                    download_dict[dl.uid()].is_torrent = True
            update_all_messages()
            LOGGER.info(f'Changed gid from {gid} to {new_gid}')
        else:
            if dl:
                threading.Thread(target=dl.getListener().onDownloadComplete).start()

    @new_thread
    def __onDownloadPause(self, api, gid):
        LOGGER.info(f"onDownloadPause: {gid}")
        dl = getDownloadByGid(gid)
        dl.getListener().onDownloadError('Download stopped by user!')

    @new_thread
    def __onDownloadStopped(self, api, gid):
        LOGGER.info(f"onDownloadStop: {gid}")
        dl = getDownloadByGid(gid)
        if dl: dl.getListener().onDownloadError('Dead torrent!')

    @new_thread
    def __onDownloadError(self, api, gid):
        sleep(0.5)  # sleep for split second to ensure proper dl gid update from onDownloadComplete
        LOGGER.info(f"onDownloadError: {gid}")
        dl = getDownloadByGid(gid)
        download = api.get_download(gid)
        error = download.error_message
        LOGGER.info(f"Download Error: {error}")
        if dl: dl.getListener().onDownloadError(error)

    def start_listener(self):
        aria2.listen_to_notifications(threaded=True, on_download_start=self.__onDownloadStarted,
                                      on_download_error=self.__onDownloadError,
                                      on_download_pause=self.__onDownloadPause,
                                      on_download_stop=self.__onDownloadStopped,
                                      on_download_complete=self.__onDownloadComplete)

    def add_download(self, link: str, path, listener, filename):
        if is_magnet(link):
            download = aria2.add_magnet(link, {'dir': path, 'out': filename})
        else:
            download = aria2.add_uris([link], {'dir': path, 'out': filename})
        if download.error_message:  # no need to proceed further at this point
            listener.onDownloadError(download.error_message)
            return
        with download_dict_lock:
            download_dict[listener.uid] = AriaDownloadStatus(download.gid, listener)
            LOGGER.info(f"Started: {download.gid} DIR:{download.dir} ")
        self.listener = listener
