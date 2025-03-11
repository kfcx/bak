import React from 'react';
import { IonContent, IonHeader, IonToolbar, IonTitle } from '@ionic/react';

const Readme = () => {
  return (
      <IonContent fullscreen>
          <IonToolbar>
            <IonTitle>开源项目介绍</IonTitle>
          </IonToolbar>
        <div className="page-main-card">
          <h1>Streaming Media Server Pro</h1>
          <p>
            <a href="https://github.com/239144498/Streaming-Media-Server-Pro"  target="opentype"> 项目地址：https://github.com/239144498/Streaming-Media-Server-Pro</a>
          </p>
          <p>
              &emsp;&emsp;这是一个强大的IPTV源后端服务,具有视频缓冲区功能,程序内置了很多独家频道,不够？你还可以自定义添加电视源；超多功能接口,还可以添加你的代理,并且适合分布式部署,非常适合作为家庭影院的IPTV服务！可玩性超高,更多详情<a href="https://github.com/239144498/Streaming-Media-Server-Pro"  target="opentype">点击链接查看</a>。
          </p>
          <p>
          &emsp;&emsp;My Blog: <a href="https://www.cnblogs.com/1314h/"  target="opentype">https://www.cnblogs.com/1314h</a>
          </p>
          <p>
          &emsp;&emsp;My GitHub: <a href="https://github.com/239144498/"  target="opentype">https://github.com/239144498</a>
          </p>
          <p>
          &emsp;&emsp;Created by Naihe,  Email:
            <a href= "mailto:239144498@qq.com">
              239144498@qq.com
            </a>
          </p>
          <h3 dir="auto">📋 打赏名单 Donation List</h3>
          <p dir="auto">非常感谢「 <a href="https://github.com/239144498/Streaming-Media-Server-Pro/wiki/Donation-List">这些用户</a> 」对本项目的赞助支持！</p>
          <h3 dir="auto">
            <a id="user-content--打赏-donation" href="https://github.com/luolongfei/freenom#-赞助-donation">
              </a>❤ 打赏 Donation
          </h3>
          <p dir="auto">&emsp;&emsp;如果你觉得本项目对你有帮助，请考虑打赏本项目，以激励我投入更多的时间进行维护与开发。 If you find this project helpful, please consider supporting the project going forward. Your support is greatly appreciated.</p>
          <p >
          <img src="https://ik.imagekit.io/naihe/pay/zsm.png" width="65%" height="65%" alt="" ></img>
          </p>
          <p>
            <strong>&emsp;&emsp;你在GitHub给的<code>star</code>或者<code>赞助</code>是我长期维护此项目的动力所在，由衷感谢每一位支持者，&ldquo;每一次你花的钱都是在为你想要的世界投票&rdquo;。 另外，将本项目推荐给更多的人，也是一种支持的方式，用的人越多更新的动力越足。</strong>
          </p>
          <p>
          </p>
        </div>
      </IonContent>
  );
};

export default Readme;
