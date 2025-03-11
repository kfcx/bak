import React from 'react';
import {Epg as EpgContainer, Layout} from "planby";
import {useApp} from "./useApp";
import Timeline from "../components/Timeline";
import {ChannelItem} from "../components/ChannelItem";
import {ProgramItem} from "../components/ProgramItem";
import styles from "../theme/Epg.module.scss";
import Button from "../components/Button";
import IconButton from "../components/IconButton";
import ChevronRight from "../icons/ChevronRight";
import ChevronLeft from "../icons/ChevronLeft";
import {useTranslation} from "react-i18next";
import useBreakpoint, {Breakpoint} from "../hooks/useBreakpoint";
import "../theme/styles.css";
// import Spinner from "../components/Spinner";


const Epgs = () => {
    const breakpoint = useBreakpoint();
    const {t} = useTranslation('common');

    const isMobile = breakpoint < Breakpoint.sm;
    const sidebarWidth = isMobile ? 70 : 184;
    const channelItemWidth = isMobile ? sidebarWidth - 10 : sidebarWidth - 24;
    const itemHeight = isMobile ? 80 : 106;

    const {getEpgProps, getLayoutProps, onScrollToNow, onScrollLeft, onScrollRight, onScrollTop, isLoading} = useApp(
        sidebarWidth,
        itemHeight,
    );

    return (
        <div className={styles.epg}>
            <div className={styles.timelineControl}>
                <Button className={styles.timelineNowButton} variant="contained" label={t('now')}
                        color="primary"
                        onClick={onScrollToNow} size="small"/>
                <IconButton className={styles.leftControl} aria-label={t('slide_left')}
                            onClick={() => onScrollLeft()}>
                    <ChevronLeft/>
                </IconButton>
                <IconButton className={styles.rightControl} aria-label={t('slide_right')}
                            onClick={() => onScrollRight()}>
                    <ChevronRight/>
                </IconButton>
            </div>
            <div style={{height: "80vh", width: "100%"}}>
                <EpgContainer isLoading={isLoading} {...getEpgProps()}>
                    <Layout
                        {...getLayoutProps()}
                        renderTimeline={(props) => <Timeline {...props} />}
                        renderProgram={({program, ...rest}) => (
                            <ProgramItem key={program.data.id} program={program} compact={isMobile} {...rest} />
                        )}
                        renderChannel={({channel}) => (
                            <ChannelItem key={channel.uuid} channel={channel}
                                         channelItemWidth={channelItemWidth}
                                         sidebarWidth={sidebarWidth}/>
                        )}
                    />
                </EpgContainer>
            </div>
        </div>
    );
}


export default Epgs;
