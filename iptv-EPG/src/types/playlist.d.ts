import type { MediaOffer } from './media';

export type GetPlaylistParams = { page_limit?: string; related_media_id?: string; token?: string; search?: string };

export type Image = {
  src: string;
  type: string;
  width: number;
};

export type Source = {
  file: string;
  type: string;
};

export type Track = {
  file: string;
  kind: string;
  label?: string;
};

export type PlaylistItem = {
  description: string;
  duration: number;
  feedid: string;
  image: string;
  images: Image[];
  link: string;
  genre?: string;
  mediaid: string;
  pubdate: number;
  rating?: string;
  requiresSubscription?: string | null;
  sources: Source[];
  seriesId?: string;
  episodeNumber?: string;
  seasonNumber?: string;
  tags?: string;
  trailerId?: string;
  title: string;
  tracks?: Track[];
  variations?: Record<string, unknown>;
  free?: string;
  productIds?: string;
  mediaOffers?: MediaOffer[] | null;
  contentType?: string;
  liveChannelsId?: string;
  scheduleUrl?: string | null;
  scheduleToken?: string;
  scheduleDataFormat?: string;
  scheduleDemo?: string;
  catchupHours?: string;
};

export type Link = {
  first?: string;
  last?: string;
};

export type Playlist = {
  description?: string;
  feed_instance_id?: string;
  feedid?: string;
  kind?: string;
  links?: Link;
  playlist: PlaylistItem[];
  title: string;
  contentType?: string;
};
