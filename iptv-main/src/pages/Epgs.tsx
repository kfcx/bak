import "../theme/styles.css";
import {Epg, Layout} from "planby";
import {useApp} from "./useApp";
import { Timeline } from "../components/Timeline";
import { ChannelItem } from "../components/ChannelItem";
import { ProgramItem } from "../components/ProgramItem";
import {IonHeader, IonPage, IonToolbar, IonTitle, IonContent} from '@ionic/react';


const Epgs = () => {
    const {isLoading, getEpgProps, getLayoutProps} = useApp();
    // console.log(isLoading, {...getEpgProps()}, {...getLayoutProps()});//, {...getLayoutProps()}

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>EPG节目单</IonTitle>
                </IonToolbar>
            </IonHeader>
            <IonContent fullscreen>
                <IonHeader collapse="condense">
                    <IonToolbar>
                        <IonTitle size="large">EPG节目单</IonTitle>
                    </IonToolbar>
                </IonHeader>
                <div>
                    {/*<div style={{ height: '600px', width: '1200px' }}>*/}
                    <div style={{height: "80vh", width: "100%"}}>
                        <Epg isLoading={isLoading} {...getEpgProps()}>
                            <Layout
                                {...getLayoutProps()}
                                renderTimeline={(props) => <Timeline {...props} />}
                                renderProgram={({program, ...rest}) => (
                                    <ProgramItem key={program.data.id} program={program} {...rest} />
                                )}
                                renderChannel={({channel}) => (
                                    <ChannelItem key={channel.uuid} channel={channel}/>
                                )}
                            />
                        </Epg>
                    </div>
                </div>
            </IonContent>
        </IonPage>
    );
}

export default Epgs;
