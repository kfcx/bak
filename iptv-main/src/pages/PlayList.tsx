import {
  IonButton,
  IonButtons,
  IonCard,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonItem,
  IonLabel,
  IonList,
  IonPage,
  IonThumbnail,
  IonTitle,
  IonToolbar,
  isPlatform,
  IonBadge
} from "@ionic/react";
import "../theme/PlayList.css";
import parser, { PlaylistItem } from "iptv-playlist-parser";
import { useCallback, useEffect, useState, useMemo } from "react";
import { search } from "ionicons/icons";
import { useSearchStore } from "../store";
import { useLocation } from "react-router";
// import ConnectStatus from "../components/ConnectStatus";

const useQuery = () => {
  const { search } = useLocation();
  return useMemo(() => new URLSearchParams(search), [search]);
};

const PlayList: React.FC = () => {
  const query = useQuery();
  const name = useMemo(() => query.get("name") || "", [query]);
  const CHINA_SOURCE = `http://vid.run.goorm.io/program?name=${name || "channel2"}`;
  const [list, setList] = useState<PlaylistItem[]>([]);
  const [data, setData] = useState<PlaylistItem[]>([]);
  // const [loading, setLoading] = useState(false);
  const [isInfiniteDisabled, setInfiniteDisabled] = useState(false);
  const setSearchList = useSearchStore((state) => state.setList);

  const pushData = useCallback(() => {
    const newData = list.slice(data.length, data.length + 21);
    setData([...data, ...newData]);
  }, [data, list]);

  const loadData = useCallback(
    (ev: any) => {
      setTimeout(() => {
        pushData();
        ev.target.complete();
        if (data.length >= list.length) {
          setInfiniteDisabled(true);
        }
      }, 500);
    },
    [data.length, list.length, pushData]
  );

  const initData = useCallback((list: PlaylistItem[]) => {
    setData(list.slice(0, 21));
  }, []);

  useEffect(() => {
    const getList = async () => {
      // setLoading(true);
      try {
          const res = await fetch(CHINA_SOURCE, {
            headers: {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS',
              'Access-Control-Allow-Headers': '*',
            }
          });
          console.log(res.status);
          const resText = await res.text();
          if (res.status === 503){
            alert("网站正在维护中，请稍后重试。")
          }else if (res.status !== 200){
            alert(resText)
          }
          const parsed = parser.parse(resText);
          const protomatch = /^(https?|ftp):/;
          const items = parsed.items.map((item) => ({
            ...item,
            url: item.url.replace(protomatch, ""),
          }));
          setList(items);
          setSearchList(items);
          if (data.length === 0) initData(items);
          // setLoading(false);
      }catch (err){
        alert("网站正在维护中，请稍后重试。")
      }
    };
    getList();
  }, [data.length, initData, setSearchList, CHINA_SOURCE]);

  return (
    <IonPage className="app-play-list">
      <IonHeader>
        <IonToolbar>
          <IonTitle>Streaming Media Server Pro 项目体验</IonTitle>
          <IonButtons collapse={true} slot="end">
            <IonButton routerLink="/page/list/search">
              <IonIcon
                size={isPlatform("ios") ? "small" : "large"}
                slot="icon-only"
                icon={search}
              />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">IPTV 项目体验</IonTitle>
            <IonButtons slot="end">
              <IonButton routerLink="/page/list/search">
                <IonIcon slot="icon-only" icon={search} />
              </IonButton>
            </IonButtons>
          </IonToolbar>
        </IonHeader>
        {isPlatform("ios") ? (
          <div className="page-main-card">
            <IonList>
              {data.map((item) => (
                <IonItem
                  key={item.url}
                  routerLink={`/page/list/player/${encodeURIComponent(
                    item.name
                  )}?url=${btoa(item.url)}`}
                >
                  <IonThumbnail slot="start">
                    <img
                      className="thumb-nail-img"
                      src={
                        item.tvg.logo
                          ? item.tvg.logo
                          : "https://placehold.jp/24/424242/ffffff/56x56.png?text=TV"
                      }
                      alt={`${item.name}_logo`}
                    />
                  </IonThumbnail>
                  <IonLabel>{item.name}</IonLabel>
                  <IonBadge class="status-badge" color="success"> Live Streaming </IonBadge>
                  {/* <ConnectStatus url={item.url} /> */}
                </IonItem>
              ))}
            </IonList>
            <IonInfiniteScroll
              onIonInfinite={loadData}
              disabled={isInfiniteDisabled}
            >
              <IonInfiniteScrollContent loadingSpinner="dots"></IonInfiniteScrollContent>
            </IonInfiniteScroll>
          </div>
        ) : (
          <IonCard className="page-main-card">
            <IonCardContent>
              <IonList>
                {data.map((item) => (
                  <IonItem
                    key={item.url}
                    routerLink={`/page/list/player/${encodeURIComponent(
                      item.name
                    )}?url=${btoa(item.url)}`}
                  >
                    <IonThumbnail slot="start">
                      <img
                        className="thumb-nail-img"
                        src={
                          item.tvg.logo
                            ? item.tvg.logo
                            : "https://placehold.jp/24/424242/ffffff/56x56.png?text=TV"
                        }
                        alt={`${item.name}_logo`}
                      />
                    </IonThumbnail>
                    <IonLabel>{item.name}</IonLabel>
                    <IonBadge class="status-badge" color="success"> Live Streaming </IonBadge>
                    {/* <ConnectStatus url={item.url} /> */}
                  </IonItem>
                ))}
              </IonList>
              <IonInfiniteScroll
                onIonInfinite={loadData}
                disabled={isInfiniteDisabled}
              >
                <IonInfiniteScrollContent loadingSpinner="dots"></IonInfiniteScrollContent>
              </IonInfiniteScroll>
            </IonCardContent>
          </IonCard>
        )}
      </IonContent>
    </IonPage>
  );
};

export default PlayList;
