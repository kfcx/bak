import * as React from "react";

import { useEpg } from "planby";
import { channels } from "../helpers/channels";
import { theme } from "../helpers/theme";
import { epg } from "../helpers/epg";

const fetchChannels = async () =>
  new Promise((res) => setTimeout(() => res(channels), 400));

const fetchEpg = async () =>
  new Promise((res) => setTimeout(() => res(epg), 500));

export function useApp() {
  const [channels, setChannels] = React.useState([]);
  const [epg, setEpg] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  const channelsData = React.useMemo(() => channels, [channels]);
  const epgData = React.useMemo(() => epg, [epg]);

  const { getEpgProps, getLayoutProps } = useEpg({
    channels: channelsData,
    epg: epgData,
    dayWidth: 7200,
    sidebarWidth: 100,
    itemHeight: 80,
    isSidebar: true,
    isTimeline: true,
    isLine: true,
    startDate: "2022-05-25T00:00:00",
    endDate: "2022-05-25T24:00:00",
    isBaseTimeFormat: true,
    theme,
    height: 500,
    width: 600
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

  return { getEpgProps, getLayoutProps, isLoading };
}
