import React  from 'react';
import { useEpg } from "planby";
import { channels } from "../helpers/channels";
import { theme } from "../helpers/theme";
import { epg } from "../helpers/epg";

const fetchChannels = async () =>
  new Promise((res) => setTimeout(() => res(channels), 400));

const fetchEpg = async () =>
  new Promise((res) => setTimeout(() => res(epg), 500));


export function useApp(sidebarWidth: number, itemHeight: number) {
  const [channels, setChannels] = React.useState([]);
  const [epg, setEpg] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  const channelsData = React.useMemo(() => channels, [channels]);
  const epgData = React.useMemo(() => epg, [epg]);

  // console.log(window.screen.height, window.screen.width)
  // console.log(window.screen.availHeight, window.screen.availWidth, window.screen.height, window.screen.width)
  console.log(window.devicePixelRatio, window.screen.height * (1 - window.devicePixelRatio), window.screen.height, window.screen.width)
  const { getEpgProps, getLayoutProps, onScrollToNow, onScrollLeft, onScrollRight, onScrollTop } = useEpg({
    channels: channelsData,
    epg: epgData,
    dayWidth: 7200,
    sidebarWidth: sidebarWidth,
    itemHeight: itemHeight,
    isSidebar: true,
    isTimeline: true,
    isLine: true,
    startDate: "2022-09-18T00:00:00",
    endDate: "2022-09-18T24:00:00",
    isBaseTimeFormat: false,
    theme,
    height: window.screen.height * (window.devicePixelRatio),
    width: window.screen.width * (window.devicePixelRatio),
  });


  const handleFetchResources = React.useCallback(async () => {
    setIsLoading(true);
    const epg: any = await fetchEpg();
    const channels: any = await fetchChannels();
    setEpg(epg);
    setChannels(channels);
    setIsLoading(false);
  }, []);

  React.useEffect(() => {
    handleFetchResources();
  }, [handleFetchResources]);

  return { getEpgProps, getLayoutProps, onScrollToNow, onScrollLeft, onScrollRight, onScrollTop, isLoading};
}