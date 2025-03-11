import {
    useProgram
} from "planby";
import {useTranslation} from 'react-i18next';
import styles from '../theme/EpgProgramItem.module.scss';
import classNames from 'classnames';

export const ProgramItem = ({program, compact, ...rest}: any) => {
    const {styles: {position}, formatTime, set12HoursTimeFormat, isLive, isMinWidth} =
        useProgram({
            program,
            ...rest,
        });
    const {t} = useTranslation('common');
    const {data} = program;
    const {image, title, since, till} = data;

    const sinceTime = formatTime(since, set12HoursTimeFormat()).toLowerCase();
    const tillTime = formatTime(till, set12HoursTimeFormat()).toLowerCase();

    const showImage = !compact && isMinWidth;
    const showLiveTagInImage = !compact && isMinWidth && isLive;

    return (
        <div className={styles.epgProgramBox} style={position} onClick={() => program}>
            <div
                className={classNames(styles.epgProgram, {
                    [styles.selected]: false,
                    [styles.live]: isLive,
                    [styles.disabled]: false,
                })}
                style={{width: styles.width}}
                data-testid={program.data.id}
            >
                {showImage && <img className={styles.epgProgramImage} src={image} alt="Preview"/>}
                {showLiveTagInImage && <div className={styles.epgLiveTag}>{t('live')}</div>}
                <div className={styles.epgProgramContent}>
                    {compact && isLive && <div className={styles.epgLiveTag}>{t('live')}</div>}
                    <h3 className={styles.epgProgramTitle}>{title}</h3>
                    <span className={styles.epgProgramText}>
            {sinceTime} - {tillTime}
          </span>
                </div>
            </div>
        </div>
    );
};
