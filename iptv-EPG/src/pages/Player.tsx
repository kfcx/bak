import {
  IonBackButton,
  IonButtons,
  IonCard,
  IonCardContent,
  IonContent,
  IonHeader,
  IonPage,
  IonTitle,
  IonToolbar,
  isPlatform,
} from "@ionic/react";
import { useParams, useLocation } from "react-router";
import "../theme/Player.css";
import { useEffect, useMemo, useRef, useCallback } from "react";

import "video.js/dist/video-js.css";
import videojs, { VideoJsPlayer, VideoJsPlayerOptions } from "video.js";

const useQuery = () => {
  const { search } = useLocation();
  return useMemo(() => new URLSearchParams(search), [search]);
};

export const VideoJS = (props: {
  options: VideoJsPlayerOptions;
  onReady?: (player: VideoJsPlayer) => void;
}) => {
  const videoRef = useRef(null);
  const playerRef = useRef<VideoJsPlayer | null>(null);
  const { options, onReady } = props;
  
  useEffect(() => {
    // Make sure Video.js player is only initialized once
    if (!playerRef.current) {
      const videoElement = videoRef.current;

      if (!videoElement) return;

      const player = (playerRef.current = videojs(videoElement, options, () => {
        videojs.log("player is ready");
        onReady && onReady(player);
      }));

      // You could update an existing player in the `else` block here
      // on prop change, for example:
    } else {
      // const player = playerRef.current;
      // player.autoplay(options.autoplay);
      // player.src(options.sources);
    }
  }, [onReady, options, videoRef]);

  // Dispose the Video.js player when the functional component unmounts
  useEffect(() => {
    const player = playerRef.current;

    return () => {
      if (player) {
        player.dispose();
        playerRef.current = null;
      }
    };
  }, [playerRef]);

  return (
    <div data-vjs-player>
      <video ref={videoRef} className="video-js vjs-big-play-centered" />
    </div>
  );
};

// 主函数入口
const Player: React.FC = () => {
  const params = useParams<{ name?: string }>();
  const query = useQuery();
  const playerRef = useRef(null);

  const url = useMemo(() => atob(query.get("url") || ""), [query]);
  const videoJsOptions = useMemo(
    () => ({
      nativeControlsForTouch: true,
      inactivityTimeout: 3, // 交互超时隐藏控件
      autoSetup: false,  // 阻止播放器为媒体元素运行
      suppressNotSupportedError: true,  //  true，则不会立即触发不兼容源错误
      noUITitleAttributes: true,
      liveui: true, // 回看进度条
      // liveTracker: {
      //   trackingThreshold: 60,
      //   liveTolerance: 15,
      // },
      poster: "//blog.naihe.cf/images/wx.png", // 视频封面图地址
      notSupportedMessage: '此视频暂无法播放，请稍后再试',
      aspectRatio: '16:9',
      autoplay: false,
      playbackRates: [0.5, 0.8, 1.0, 1.2, 1.5, 1.7, 2],
      controls: true, // 是否显示控制条
      responsive: true,
      language: 'zh-CN', // 设置语言
      fluid: true, // 自适应宽高
      muted: false, // 是否静音
      sources: [
        {
          src: url,
          type: "application/x-mpegURL",
        },
      ],
      controlBar: { // 设置控制条组件
        volumePanel: {
          inline: false //默认是true,横着的
        },
        timeDivider: true, // 当前时间和持续时间的分隔符
        durationDisplay: true, // 显示持续时间
        remainingTimeDisplay: false, // 是否显示剩余时间功能
        fullscreenToggle: true, // 是否显示全屏按钮
      }
    }),
    [url]
  );

  const handlePlayerReady = useCallback((player) => {
    playerRef.current = player;

    // player.on('error', () => {
    //   console.log('event - error')
    // })
    player.on('loadeddata', () => {
      console.log('event - loadeddata')
    })
    player.on('loadedmetadata', () => {
      console.log('event - loadedmetadata')
    })
    player.on('loadstart', () => {
      console.log('event - loadstart')
    })

    player.ready(() => {
      // 丢失 source 事件处理
      player.tech().on('retryplaylist', function () {
        console.log('event - retryplaylist!!!')
        player.pause();
        player.src({
          src: url,
          type: "application/x-mpegURL",
        });
        // player.load();
        player.play();
      })
    })

    player.on('stalled', () => {
      videojs.log('网速异常!');
    });
    player.on('seeking', () => {
      videojs.log('视频跳转中!');
    });

    player.on('playing', () => {
      videojs.log('playback began!');
    });

    // You can handle player events here, for example:
    player.on("waiting", () => {
      videojs.log("player is waiting");
    });

    player.on("dispose", () => {
      videojs.log("player will dispose");
    });
  }, [url]);

  return (
    <IonPage className="page-player">
      <IonHeader translucent>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton />
          </IonButtons>
          <IonTitle>
            {params.name ? decodeURIComponent(params.name) : "Player"}
          </IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent fullscreen>
        {isPlatform("ios") ? (
          <div className="player-main-card">
            <VideoJS options={videoJsOptions} onReady={handlePlayerReady} />
          </div>
        ) : (
          <IonCard className="player-main-card">
            <IonCardContent>
              <VideoJS options={videoJsOptions} onReady={handlePlayerReady} />
            </IonCardContent>
          </IonCard>
        )}
      </IonContent>
    </IonPage>
  );
};

export default Player;
