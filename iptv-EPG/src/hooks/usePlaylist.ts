// import { generatePlaylistPlaceholder } from '../utils/collection';
import { queryClient } from '../providers/QueryProvider';
import { getDataOrThrow } from '../utils/api';
import type { Playlist } from '../types/playlist';

// const placeholderData = generatePlaylistPlaceholder(30);

const getPlaylistById = async (): Promise<Playlist | undefined> => {
  const url = "http://baidu.com"
  const response = await fetch(url);
  const data = await getDataOrThrow(response);
  return data;
};

const usePlaylist = async () => {
    const playlist = await getPlaylistById();

    // This pre-caches all playlist items and makes navigating a lot faster. This doesn't work when DRM is enabled
    // because of the token mechanism.
    playlist?.playlist?.forEach((playlistItem) => {
      queryClient.setQueryData(['media', playlistItem.mediaid, {}, undefined], playlistItem);
    });

    return playlist;
  };

export default usePlaylist
