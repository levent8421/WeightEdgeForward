
/**
 * Create By Levent8421
 * Create Time: 2021/5/15 18:12
 * Class Name: MessageActions
 * Author: Levent8421
 * Description:
 * 消息Action定义
 *
 * @author Levent8421
 */
public class MessageActions {
    /**
     * 版本信息
     */
    public static class Version {
        public static final String V01 = "V0.1";
        public static final String V02 = "V0.2";
    }

    /**
     * 心跳
     */
    public static final String HEARTBEAT = "notify.heartbeat";
    /**
     * 启动
     */
    public static final String STARTUP = "notify.startup";
    /**
     * 获取服务状态 IMOK
     */
    public static final String RUOK = "ruok.get";
    /**
     * 设置逻辑货道号
     */
    public static final String SET_SLOT_NO = "balance.no.set";
    /**
     * 设置货道SKU
     */
    public static final String SET_SLOT_SKU = "balance.sku.set";
    /**
     * 温湿度时间窗口数据主动上报
     */
    public static final String TH_SENSOR_DATA_WINDOWS = "notify.th_sensor.window_records";
    /**
     * 温湿度传感器参数设置
     */
    public static final String TH_SENSOR_SETTING = "th_sensor.set_params";
    /**
     * 温湿度传感器状态改变
     */
    public static final String TH_SENSOR_STATE_CHANGED = "notify.th_sensor.status";
    /**
     * 重力货道状态变化上百
     */
    public static final String SCALE_SLOT_STATE_CHANGED = "notify.balance.state";
    /**
     * 重力货道重量变化通知
     */
    public static final String SCALE_SLOT_WEIGHT_CHANGED = "notify.balance.weight_changed";
    /**
     * 查询货道数据
     */
    public static final String SCALE_SLOT_DATA_GET = "balance.data.get";
    /**
     * 查询货道分组信息
     */
    public static final String SCALE_SLOT_GROUPS_GET = "balance.groups.get";
    /**
     * 重力货道合并通知
     */
    public static final String SCALE_SLOT_MERGED = "notify.balance.merged";
    /**
     * 重力货道拆分通知
     */
    public static final String SCALE_SLOT_UNMERGED = "notify.balance.unmerged";
    /**
     * 温湿度传感器数据采集
     */
    public static final String TH_SENSOR_DATA_GET = "thsensor.data.get";
    /**
     * 通知温湿度时间点数据
     */
    public static final String NOTIFY_TH_SENSOR_POINT_RECORDS = "notify.th_sensor.point_records";
    /**
     * 设置货道停用、启用
     */
    public static final String SCALE_SLOT_ENABLE_SET = "balance.valid.set";
    /**
     * 设置温湿度传感器启用禁用
     */
    public static final String TH_SENSOR_ENABLE_SET = "th_sensor.enable_set";

}
