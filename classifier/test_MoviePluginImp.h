#ifndef  __TESTMOVIEPLUGIN_H_
#define  __TESTMOVIEPLUGIN_H_

#include "test_MoviePluginImp.h"
#include <fstream>
#include "json/json.h"
#include "JsonObj.h"
#include <string>
#include <GremlinServerConnect.h>
#include <ServiceApiServerConnect.h>
#include <vector>
#include "sofa/kernel/box.h"
namespace movie_plugin{
namespace btest{

class test_MoviePluginImp
{
public:
//判断当天是否属于周几到周几的星期范围
bool test_MoviePluginImp::is_date_in_week(const struct tm *ptm,const std::string& week1,const std::string& week2) {
    std::stringstream ss;
    ss<<ptm->tm_wday;
    std::string week = ss.str();
    CDEBUG_LOG("today %s ; week1 %s ; week2 %s",week.c_str(),week1.c_str(),week2.c_str());
    return (week>=week1 && week<=week2);
}
//对于只有春夏秋冬没有具体时间范围的数据，判断当天是否在季节之内
bool test_MoviePluginImp::is_date_in_season(const std::string& date,const std::string& season_str) {
    if (date.size() != 4 || date > "1231") {
        return false;
    } else if (date >= "1201") {
        return season_str.find("冬") != std::string::npos;
    } else if (date >= "0901") {
        return season_str.find("秋") != std::string::npos;
    } else if (date >= "0601") {
        return season_str.find("夏") != std::string::npos;
    } else if (date >= "0301") {
        return season_str.find("春") != std::string::npos;
    } else if (date >= "0101") {
        return season_str.find("冬") != std::string::npos;
    } else {
        return false;
    }
}
//判断当天是否属于两个时间以内。时间数据分为两种情况，一是03~05，二是0301~0513；每种情况有两种数据，一是03~05，二是11~03，第二种数据03指的是次年
bool test_MoviePluginImp::is_date_in_period(const std::string &date,const std::string &start,const std::string &end) {
    std::string start_date = start;
    std::string end_date = end;
    static std::string last_day[12] = {"31","29","31","30","31","30","31","31","30","31","30","31"};
    if (start_date.size() == 2) {
        start_date += "01";
    }
    if (end_date.size() == 2) {
        end_date += last_day[atoi(end_date.c_str())-1];
    }
    
    if (start_date.size() != 4 || end_date.size() != 4) {
        return false;
    }
    
    if (start_date <= end_date) {
        return start_date <= date && date <= end_date;
    } else {
        return is_date_in_period(date, start_date, "1231") || is_date_in_period(date, "0101", end_date);
    }
}
//判断是否在指定的节假日内
bool test_MoviePluginImp::is_date_in_holiday(const struct tm *ptm,const std::vector<std::string> &holidays) {
    char today [9];
    strftime(today, sizeof(today), "%G%m%d",ptm);
    std::string holiday;
    for (unsigned int i=0; i<holidays.size(); i++) {
        holiday += "\""+holidays[i]+"\",";
    }
    holiday.erase(holiday.end()-1);
    //节假日
    faci::knowledge::ServiceApiServerConnect* gremlinConnect = faci::knowledge::ServiceApiServerConnect::getConn();
    ::sofa::ObjectPtr __ret;
    ::sofa::ObjectPtr extra_info;
    std::string spo_query = "search_holiday(date_from_string(\""+std::string(today)+"\"), ["+holiday+"])";
    int req = gremlinConnect->computeQuery(spo_query, __ret, extra_info, "person");
    CDEBUG_LOG("sa_spo : %d", req);
    CDEBUG_LOG("spo_query : %s \t %s",holiday.c_str(), spo_query.c_str());
    std::string result = ::sofa::unbox<std::string>(__ret);
    faci::graphsearch::Json element;
    element.fromString(result);
    CDEBUG_LOG("date in result process\t%s\t%d", result.c_str(), element.size());
    if (element.isNull() || !element.isMember("data") || !element["data"].isString()) {
         CWARNING_LOG("kc request to check holidays failed.");
         return false;
    } else {
         return (element["data"].asString()=="true") ? true : false;
    }
}
//计算营业时间
std::string test_MoviePluginImp::compute_today_openinghours(const struct tm *ptm,::faci::graphsearch::Json &structured_json) {
    ::faci::graphsearch::Json result = structured_json["openingHours"];
    if (result.isNull() || !result.isArray())
    {
        CDEBUG_LOG("result is null or is not array");
        return "";
    }
    std::string opentime="";
    std::string closetime="";
    for (size_t i=0; i<result.size(); i++)
    {
        ::faci::graphsearch::Json tmp = result[i];
        bool check_month = false;
        bool check_week = false;
        bool has_month = false;
        bool has_week = false;
        if (tmp.isMember("month")) {
            has_month = true;
            //有具体时间范围，判断时间区间
            char today [9];
            strftime(today, sizeof(today), "%m%d",ptm);
            std::string date(today);
            if (tmp["month"].isMember("start") && tmp["month"].isMember("end") && tmp["month"]["start"].isString() && tmp["month"]["end"].isString() && tmp["month"]["start"].asString()!="0000" && tmp["month"]["end"].asString()!="0000") {
                check_month = is_date_in_period(date,tmp["month"]["start"].asString(),tmp["month"]["end"].asString());
            }else if (tmp["month"].isMember("info") && tmp["month"]["info"].isString()) {//没有具体时间范围，判断季节区间
                check_month = is_date_in_season(date,tmp["month"]["info"].asString());
            }
        }
        //判断星期区间
        if (has_month&&check_month){
            if (tmp.isMember("week")) {
                has_week = true;
                if (tmp["week"].isMember("start") && tmp["week"].isMember("end") && tmp["week"]["start"].isString() && tmp["week"]["end"].isString()) {
                    check_week = is_date_in_week(ptm,tmp["week"]["start"].asString(),tmp["week"]["end"].asString());
                }
            }
        }
        
        if ((has_month&&check_month)&&(has_week&&check_week)&&(tmp.isMember("hour"))) {
            if (opentime=="" && tmp["hour"].isMember("opentime") && tmp["hour"]["opentime"].isString()){
                opentime = tmp["hour"]["opentime"].asString();
            }
            if (closetime=="" && tmp["hour"].isMember("closetime") && tmp["hour"]["closetime"].isString()){
                closetime = tmp["hour"]["closetime"].asString();
            }
            break;
        }
    }

    if (!structured_json.isMember("specialHours")) {
        if (opentime!="" && closetime!=""){
           return opentime + "~" + closetime;
        } else {
           return "";
        }
    }
    //有节假日信息，分为两种情况
    result = structured_json["specialHours"];
    if (result.isNull() || !result.isArray())
    {
        CDEBUG_LOG("result is null or is not array");
        return "";
    }
    bool week_close = false;
    for (size_t i=0; i<result.size(); i++)
    {
        ::faci::graphsearch::Json tmp = result[i];
        if (tmp.isMember("type") && tmp["type"].isString() && tmp.isMember("holiday") && tmp["holiday"].isArray()) {
            //std::string info="";
            std::vector<std::string> holidays;
            //关门。关门包含特殊情况，如周一关门（节假日除外），因此既是周一又是节假日需开门。
            if (tmp["type"].asString()=="close") {
                for (size_t j=0; j<tmp["holiday"].size(); j++) {
                    if (tmp["holiday"][j].isString()) {
                        if (tmp["holiday"][j].asString().find("周")==std::string::npos){
                            holidays.push_back(tmp["holiday"][j].asString());
                        }else {
                            //周
                            std::string pxq[]={"日","一","二","三","四","五","六"};
                            std::stringstream ss;
                            ss<<"周"<<pxq[ptm->tm_wday];
                            std::string week = ss.str();
                            week_close = (tmp["holiday"][j].asString().find(week)!=std::string::npos) ? true : week_close;
                        }
                    }
                }
                if (!holidays.empty()) {
                    if (is_date_in_holiday(ptm,holidays)) {
                        return "close";
                    }
                }
            }else if (tmp["type"].asString()=="open") {
                bool check = false;
                for (size_t j=0; j<tmp["holiday"].size(); j++) {
                    if (tmp["holiday"][j].isString()) {
                        if (tmp["holiday"][j].asString().find("周")==std::string::npos){
                            holidays.push_back(tmp["holiday"][j].asString());
                        }else {
                            //周
                            std::string pxq[]={"日","一","二","三","四","五","六"};
                            std::stringstream ss;
                            ss<<"周"<<pxq[ptm->tm_wday];
                            std::string week = ss.str();
                            check = (tmp["holiday"][j].asString().find(week)!=std::string::npos) ? true : check; 
                        }
                    }
                }
                if (!holidays.empty() && !check) {
                    check = is_date_in_holiday(ptm,holidays);
                }
                if (check) {
                    if (tmp.isMember("hour")) {
                        if (tmp["hour"].isMember("opentime") && tmp["hour"]["opentime"].isString()) {
                            opentime = tmp["hour"]["opentime"].asString();
                        }
                        if (tmp["hour"].isMember("closetime") && tmp["hour"]["closetime"].isString()) {
                            closetime = tmp["hour"]["closetime"].asString();
                        }
                     }
                     return opentime + "~" + closetime;
                }
            }
        }
    }
    if (week_close) {
        return "close";
    }
    if (opentime!="" && closetime!="") {
        return opentime + "~" + closetime;
    }else
        return "";
}
//计算票价
std::string test_MoviePluginImp::compute_today_price(const struct tm *ptm, ::faci::graphsearch::Json &structured_json) {
    ::faci::graphsearch::Json result = structured_json;
    if (result.isNull() || !result.isArray())
    {
        CDEBUG_LOG("result is null or is not array");
        return "";
    }
    for (size_t i=0; i<result.size(); i++)
    {
        ::faci::graphsearch::Json tmp = result[i];
        if (tmp.isMember("price") && tmp["price"].isString()) {
            if (tmp.isMember("month")) {
                //有具体时间范围，判断时间区间
                char today [9];
                strftime(today, sizeof(today), "%m%d",ptm);
                std::string date(today);
                if (tmp["month"].isMember("start") && tmp["month"].isMember("end") && tmp["month"]["start"].isString() && tmp["month"]["end"].isString()) {
                    if (is_date_in_period(date,tmp["month"]["start"].asString(),tmp["month"]["end"].asString())) {
                        return tmp["price"].asString();
                    }
                //没有具体时间范围，判断季节区间
                }else if (tmp["month"].isMember("info") && tmp["month"]["info"].isString()) {
                    if (is_date_in_season(date,tmp["month"]["info"].asString())) {
                        return tmp["price"].asString();
                    } else if (tmp["month"]["info"].asString().find("淡季")!=std::string::npos) {
                        return tmp["price"].asString()+"起";
                    }
                }
            }else {
                return tmp["price"].asString();
            }
        }
    }
    CDEBUG_LOG("This result doesn't have a field named Price");
    return "";
}

void test_MoviePluginImp::compute_scene_pc(const struct tm *ptm,::faci::graphsearch::Json& scene_json) {
    if (!scene_json.isNull() && scene_json.isMember("structured_info")) {
        ::faci::graphsearch::Json structured_json;
        structured_json = scene_json["structured_info"];
        std::string structured_str;
        structured_json.toString(structured_str);
        CDEBUG_LOG("structured_info input : %s",structured_str.c_str());
        char today [9];
        strftime(today, sizeof(today), "%G%m%d",ptm);
        std::string date(today);
        // 计算当天时间和票价
        if (structured_json.isMember("openingHours")) {
            std::string toh = compute_today_openinghours(ptm,structured_json);
            if (!toh.empty()) {
			CDEBUG_LOG("checked");
                 scene_json["todayOpeningHours"] = toh;
            }
            CDEBUG_LOG("compute_today_openinghours end : %s",toh.c_str());
        }
        if (structured_json.isMember("price")) {
            std::string toh = compute_today_price(ptm,structured_json["price"]);
            if (!toh.empty()) {
                 scene_json["todayPrice"] = toh;
            }
            CDEBUG_LOG("compute_today_price end : %s",toh.c_str());
        }
        //delete ptm;
        // 提取带换行的详细时间与票价
        if (structured_json.isMember("detailTime")) {
            scene_json["detailOpeningHours"] = structured_json["detailTime"].asString();
            CDEBUG_LOG("detailOpeningHours end : %s",structured_json["detailTime"].asString().c_str());
        }
        if (structured_json.isMember("detailPrice")) {
            scene_json["detailPrice"] = structured_json["detailPrice"].asString();
            CDEBUG_LOG("detailPrice end : %s",structured_json["detailPrice"].asString().c_str());
        }
        scene_json.removeMember("structured_info");
    }
}
};
} //namespace btest
} //namespace movie_plugin

#endif  //__TESTMOVIEPLUGIN_H_
