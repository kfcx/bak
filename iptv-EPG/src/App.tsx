import { IonApp, IonRouterOutlet, setupIonicReact } from "@ionic/react";
import { IonReactRouter } from "@ionic/react-router";
import { Redirect, Route } from "react-router-dom";

/* Core CSS required for Ionic components to work properly */
// import "@ionic/react/css/core.css";
// import "./theme/core.css";

/* Basic CSS for apps built with Ionic */
// import "@ionic/react/css/normalize.css";
// import "@ionic/react/css/structure.css";
// import "@ionic/react/css/typography.css";

/* Optional CSS utils that can be commented out */
// import "@ionic/react/css/padding.css";
// import "@ionic/react/css/float-elements.css";
// import "@ionic/react/css/text-alignment.css";
// import "@ionic/react/css/text-transformation.css";
// import "@ionic/react/css/flex-utils.css";
// import "@ionic/react/css/display.css";
//	https://agit.ai/239144498/owner/raw/branch/master/img/MOBILE/logo_4gtv_4gtv-4gtv084_mobile.png
//https://agit.ai/239144498/owner/raw/branch/master/img/MOBILE/logo_4gtv_4gtv-4gtv084_mobile_0204.png
/* Theme variables */
import "./theme/main.scss";
import styles from './theme/ErrorPage.module.scss';
import Tabs from "./pages/Tabs";

setupIonicReact();


const App: React.FC = () => {
  return (
    <IonApp>
      <IonReactRouter>
        <IonRouterOutlet id="main">
          <Route path="/page" render={() => <Tabs />} />
          <Route exact path="/">
            <Redirect to="/page" />
          </Route>
          <Route>
              <div className={styles.errorPage}>
                  <div className={styles.box}>
                    <header>
                      <h1 className={styles.title}>notfound_error_description</h1>
                    </header>
                    <main className={styles.main}>This page doesn't exist.</main>
                  </div>
            </div>
          </Route>
        </IonRouterOutlet>
      </IonReactRouter>
    </IonApp>
  );
};

export default App;
