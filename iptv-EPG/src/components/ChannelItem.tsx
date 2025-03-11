import { useEpg, Epg, Layout, ChannelBox, ChannelLogo, Channel } from 'planby';
import styles from '../theme/EpgChannelItem.module.scss';
import classNames from 'classnames';

interface ChannelItemProps {
  channel: Channel;
  channelItemWidth: number;
  sidebarWidth: number;
}

export const ChannelItem = ({ channel, channelItemWidth, sidebarWidth }: ChannelItemProps) => {
  const { position, logo, uuid } = channel;
  const style = { top: position.top, height: position.height, width: sidebarWidth };

  return (
    <div className={styles.epgChannelBox} style={style}>
      <div
        className={classNames(styles.epgChannel, { [styles.active]: true })}
        style={{ width: channelItemWidth }}
        onClick={() => console.log(channel)}
        data-testid={uuid}
      >
        <img className={styles.epgChannelLogo} src={logo} alt="Logo" />
      </div>
    </div>
  );
};
