#include <sofa.h>
#include <sofa/dev/dev.h>
#include <sofa/kernel/config.h>
#include <sofa/kernel/sync_async_conv.h>
#include <sofa/kernel/not_implement_exception.h>
#include "sofa/kernel/box.h"
#include "sofa/text/json.h"
#include <boost/thread.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
#include "JsonObj.h"
#include "MoviePluginImp.h"
#include "com_log.h"
#include "comlogplugin.h"
#include "cronoapd.h"
#include <fstream>
namespace imp {
namespace com {
namespace baidu {
namespace wd {
namespace knowledge {
namespace ver_1_0_0 {



using namespace ::com::baidu::wd::knowledge::ver_1_0_0;

//std::map<std::string,std::string>mapping_map;
std::map< std::string, std::map<std::string, std::string> > map_all;
std::map< std::string, std::map<int, std::string> > mapconf_all ;
std::vector<std::string> typelist_vector;
std::map< std::string, std::map<std::string, std::string> > mapedge_all;
std::vector<std::string> edgelist_vector;
std::map<std::string, std::string> logicname_map;
//mutil thread var
//::boost::thread_specific_ptr< gremlin::GraphQueryPtr > shandle_pool;
::boost::thread_specific_ptr< SPOThreadFifaData_t > SPOThreadFifaData_pool;

MoviePluginImp::MoviePluginImp()
{
}

MoviePluginImp::~MoviePluginImp()
{
}

bool MoviePluginImp::init(const ::sofa::Config& conf)
{
    // TODO: add init code here.
    return true;
}
inline bool split_words( std::string &input , std::string split , std::vector<std::string> *output);

int64_t MoviePluginImp::reload() {
    return 0;
}

void MoviePluginImp::async_reload(
        ::sofa::AsyncControllerPtr __cntl,
        int64_t* __ret)
{
    typedef int64_t __ret_type;
    SOFA_ASYNC_TO_SYNC(__ret_type, reload);
}

int64_t MoviePluginImp::InitOnce(
        const std::string& conf)
{
    // TODO: add implement code here.

    ::sofa::Config config;
    if(!config.load(conf)){
        CFATAL_LOG("SpoPlugin load %s failed", conf.c_str());
        return -1;
    }

    if(!config.has("log_dir") || !config.has("log_conf")){
        CFATAL_LOG("conf must have comlog conf");
        return -1;
    }

    std::string comlog_dir = config.get<std::string>("log_dir");
    std::string comlog_conf = config.get<std::string>("log_conf");
    com_registappender(
            "CRONO",
            comspace::CronoAppender::getAppender,
            comspace::CronoAppender::tryAppender
            );
    if(com_loadlog(comlog_dir.c_str(), comlog_conf.c_str())){
        CWARNING_LOG("com_log init failed");
    }
    com_reglogstat(comlog_dir.c_str(), comlog_conf.c_str());
    std::ifstream fin_map(config.get<std::string>("movie_logicname").c_str());
    if (!fin_map){
        CFATAL_LOG("zici_pluginimp load mapping_dict error");
        return 1;
    }
    std::string line;
    std::vector<std::string> tokens;
    while (getline(fin_map, line)){
        boost::split(tokens, line, boost::is_any_of(" "));
        CWARNING_LOG("logicname_dict info\t%s\t%s", tokens[0].c_str(), tokens[1].c_str());
        logicname_map.insert(std::pair<std::string, std::string>(tokens[0], tokens[1]));
    }
    std::string typelist = config.get<std::string>("typelist");
    int len = split_words(typelist, ",", &typelist_vector);
    len = typelist_vector.size();
    for (int i = 0; i < len; i++){
        std::map<std::string, std::string>mapping;
        std::map<int, std::string> mapping_conf;
        std::string type_now = typelist_vector[i];
        std::string proplist = "proplist_" + type_now;
        std::string searchp = "searchp_" + type_now;
        std::string conf = "conf_" + type_now;
        std::string proplist_str = config.get<std::string>(proplist);
        std::string searchp_str = config.get<std::string>(searchp);
        std::string conf_str = config.get<std::string>(conf);
        std::vector<std::string> proplist_vector;
        split_words(proplist_str, ",", &proplist_vector);
        int proplist_len = proplist_vector.size();
        std::vector<std::string> searchp_vector;
        split_words(searchp_str, ",", &searchp_vector);
        int searchp_len = searchp_vector.size();
        std::vector<std::string> conf_vector;
        split_words(conf_str, ",", &conf_vector);
        int conf_len = conf_vector.size();
        if (conf_len != 5){
            CFATAL_LOG("conf num error.");
            return -1;
        }
        if (proplist_len != searchp_len){
            CFATAL_LOG("type %s\t searchp and proplist don't match,proplist_len :%d\t,searchp_len :%d\t", type_now.c_str(), proplist_len, searchp_len);
            return -1;
        }
        //从配置加载展现属性到内存中
        for (int j = 0; j < proplist_len; j++){
            mapping.insert(std::pair<std::string, std::string>(proplist_vector[j], searchp_vector[j]));
            CNOTICE_LOG("mapping_dict:%s\t%s", proplist_vector[j].c_str(), searchp_vector[j].c_str());
        }
        //单实体模板，固定5个可配置的字段值
        for (int k = 0; k < 5; k++){
            mapping_conf.insert(std::pair<int, std::string>(k, conf_vector[k]));
            CNOTICE_LOG("conf_dict:%s", conf_vector[k].c_str());
        }
        map_all.insert(std::pair< std::string, std::map<std::string, std::string> >(type_now, mapping));
        mapconf_all.insert(std::pair< std::string, std::map<int, std::string> >(type_now, mapping_conf));
        //边
        std::map<std::string, std::string> mappingedge;
        std::string edgelist = "edgelist_" + type_now;
        std::string edgelistch = "edgelistch_" + type_now;
        if (config.has(edgelist)&&config.has(edgelistch)) {
            std::string edgelist_src = config.get<std::string>(edgelist);
            std::string edgelistch_src = config.get<std::string>(edgelistch);
            std::vector<std::string> edgelist_vector;
            split_words(edgelist_src, ",", &edgelist_vector);
            int edgelist_len = edgelist_vector.size();
            std::vector<std::string> edgelistch_vector;
            split_words(edgelistch_src, ",", &edgelistch_vector);
            int edgelistch_len = edgelistch_vector.size();
            if (edgelist_len != edgelistch_len) {
                CFATAL_LOG("type %s\t edgelist and edgelistch don't match,edgelist_len :%d\t,edgelistch_len :%d\t", type_now.c_str(), proplist_len, searchp_len);
                return -1;
            }
            for (int j = 0; j < edgelist_len; j++) {
                mappingedge.insert(std::pair<std::string, std::string>(edgelist_vector[j], edgelistch_vector[j]));
                CNOTICE_LOG("mappingedge_dict:%s\t%s", edgelist_vector[j].c_str(), edgelistch_vector[j].c_str());
            }
        }
        mapedge_all.insert(std::pair< std::string, std::map<std::string, std::string> >(type_now, mappingedge));
    }
    //加载配置结束
    CNOTICE_LOG("load conf ok");
    return 0;
}

void MoviePluginImp::async_InitOnce(
        ::sofa::AsyncControllerPtr __cntl,
        int64_t* __ret,
        const std::string& conf)
{
    typedef int64_t __ret_type;
    SOFA_ASYNC_TO_SYNC(__ret_type, InitOnce, conf);
}

int64_t MoviePluginImp::AcceptQuery(
        const ::com::baidu::wd::knowledge::ver_1_0_0::QueryParamPtr& query_param,
        uint64_t* handle)
{
    // TODO: add implement code here.
    //SOFA_THROW(::sofa::NotImplementException, "MoviePluginImp::AcceptQuery");
    //

    SPOThreadFifaData_t* fifadata_handle = SPOThreadFifaData_pool.get();
    if(fifadata_handle == NULL){
        fifadata_handle = new SPOThreadFifaData_t();
        SPOThreadFifaData_pool.reset(fifadata_handle);
    }
    *handle = (uint64_t)fifadata_handle;
    fifadata_handle->src_query = query_param->text_query();
    if(query_param->da_query() == "" || query_param->da_query().length() < 5){
        CFATAL_LOG("kg da query parse failed");
        return -1;
    }
    fifadata_handle->client_name = query_param->ClientName();
    fifadata_handle->norm_query = query_param->norm_query();
    //如果来源是度秘,先转成wise,并备份真实来源
    if (fifadata_handle->client_name == "du_aries")
    {
        fifadata_handle->client_name_real = fifadata_handle->client_name;
        fifadata_handle->client_name = "wise-us";
        CDEBUG_LOG("change clientname from [%s] to [%s]",fifadata_handle->client_name_real.c_str(), fifadata_handle->client_name.c_str());
    }
    else
    {
        fifadata_handle->client_name_real = "";
    }

    CNOTICE_LOG("query_param->client_name : %s", query_param->ClientName().c_str());
    CNOTICE_LOG("namedalog daquery daextra %s\t%s",
            query_param->da_query().c_str(), query_param->da_extra().c_str());
    CDEBUG_LOG("%s : %s : %lu", fifadata_handle->src_query.c_str(), query_param->da_query().c_str(), (uint64_t)fifadata_handle);
    fifadata_handle->spo_query = query_param->da_query();
    std::string search_prop = query_param->da_extra();
    fifadata_handle->search_prop = search_prop;
    fifadata_handle->srcid = (int)query_param->srcid();

    if (true)
    {
        std::string da_query;
       //加载json字符串
        faci::graphsearch::Json qu_ret;
        qu_ret.fromString(fifadata_handle->spo_query);
        if (!qu_ret.isNull() 
            && qu_ret.isMember("result")
            && qu_ret["result"].isArray() 
            && qu_ret["result"].size()>0 
            && qu_ret["result"][(size_t)0].isMember("cmd"))
        {
            da_query = qu_ret["result"][(size_t)0]["cmd"].asString();
        }
        else
        {
            CFATAL_LOG("query:%s get proprerty failed", fifadata_handle->src_query.c_str());
            return -1;
        }
   
        //按#切割
        std::vector<std::string> result;
        boost::split(result, da_query, boost::is_any_of("#"));
        if (result.size()!=2)
        {
            CFATAL_LOG("query:%s get proprerty failed", fifadata_handle->src_query.c_str());
            return -1;
        }
        fifadata_handle->spo_query = result[0];
        fifadata_handle->search_prop = result[1];
        CDEBUG_LOG("da_query:%s  search_prop:%s", fifadata_handle->spo_query.c_str(), 
                                                  fifadata_handle->search_prop.c_str());
    }

    return 0;
}

void MoviePluginImp::async_AcceptQuery(
        ::sofa::AsyncControllerPtr __cntl,
        int64_t* __ret,
        const ::com::baidu::wd::knowledge::ver_1_0_0::QueryParamPtr& query_param,
        uint64_t* handle)
{
    typedef int64_t __ret_type;
    SOFA_ASYNC_TO_SYNC(__ret_type, AcceptQuery, query_param, handle);
}
inline bool split_words( std::string &input , std::string split , std::vector<std::string> *output){
    if (output == NULL){
        CFATAL_LOG("split_output point is null");
        return -1;
    }
    size_t pos_end = 0;
    size_t pos_start = 0;
    while (std::string::npos != (pos_end = input.find_first_of(split,pos_start))){
        (*output).push_back(input.substr(pos_start, pos_end - pos_start));
        pos_start = pos_end + 1;
    }
    if (pos_start <= input.size() - 1){
        (*output).push_back(input.substr(pos_start, input.size() - pos_start));
    }
    return (*output).size() > 0;
}

inline int string_to_int(std::string &input){
    int result = -1;
    std::stringstream tmp_ss;
    tmp_ss << input;
    tmp_ss >> result;
    CNOTICE_LOG("return result is %d", result);
    return result;

}

int64_t MoviePluginImp::DoQuery(
        uint64_t handle,
        ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr >* result,
        ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr >* kg_res)
{

    KgCardPtr card = ::sofa::create< KgCard >();
    std::string* response = &(card->content());
    // faci::knowledge::GremlinServerConnect* gremlinConnect =
    //         faci::knowledge::GremlinServerConnect::getConn();
    faci::knowledge::ServiceApiServerConnect* gremlinConnect =
            faci::knowledge::ServiceApiServerConnect::getConn();

    struct SPOThreadFifaData_t* fifadata_handle = (struct SPOThreadFifaData_t*)handle;

    //fifadata_handle->spo_query = "g.query().has('nid',MATCH,'1830815438946293842').with('*')";
    CDEBUG_LOG("namedagremlin_beforesearch\t%s", fifadata_handle->spo_query.c_str());
    std::string resource_name;
    if (logicname_map.find(fifadata_handle->search_prop)!= logicname_map.end()){
        resource_name = logicname_map[fifadata_handle->search_prop];
        // fifadata_handle->spo_query = "g.has('logicname', MATCH, '"
        //     + logicname_map[fifadata_handle->search_prop] + "')"
        //     + fifadata_handle->spo_query.substr(9);
        // CDEBUG_LOG("namedagremlin_add_logicname\t%s", fifadata_handle->spo_query.c_str());
    }
    else{
        //配置没有指定的属性 默认查default指定的库
        resource_name = logicname_map["default"];
        // fifadata_handle->spo_query = "g.has('logicname', MATCH, '"
        //     + logicname_map["default"] + "')"
        //     + fifadata_handle->spo_query.substr(9);
        // CDEBUG_LOG("namedagremlin_add_logicname\t%s", fifadata_handle->spo_query.c_str());
    }
    ::sofa::ObjectPtr __ret;
    ::sofa::ObjectPtr extra_info;
    gremlinConnect->gremlinQuery(fifadata_handle->spo_query, __ret, extra_info, resource_name);

    faci::graphsearch::Json element(__ret);
    std::string tmp_result;
    std::string name;
    std::string jump_url = "lvyou.baidu.com";
    std::string result_type = "default_type";
    std::string search_property = fifadata_handle->search_prop;
    element.toString(tmp_result);
    std::string search_edge = "";
    std::string title_name = "";
    CDEBUG_LOG("search result_before process\t%s\t%d", tmp_result.c_str(), element.size());
    if(element.isNull()){
        return -3;
    }
    int process_loc = -1 ;
    int year = 0;
    int  month = 0;
    int scene_hot=0;
    for (size_t k = 0; k < element.size(); ++k){
        //属性类的唯一结果不排序了
        if (element.isArray() && element.size()==1 && fifadata_handle->spo_query.find("out") == std::string::npos)
        {
            process_loc = 0;
            break;
        }
        if (element.isArray() && element[k].isMember("type") && element[k]["type"].isArray()) {
            result_type = element[k]["type"][(size_t)0].asString();
            CDEBUG_LOG("type is %s", result_type.c_str());
            std::vector<std::string>::iterator s = find(typelist_vector.begin(),
                    typelist_vector.end(), result_type);
            if (s != typelist_vector.end()){
                //通用冲突处理逻辑在此
                //1.返回多实体结果 只处理配置中的类型
                //2.返回多个可处理类型 只处理数据中包含查询属性的结果
                //2.eg 故宫门票 处理含有price属性的景点类型 不处理电影类型
                CNOTICE_LOG("find process_type:%s ,k:%d", result_type.c_str(), k);
                CDEBUG_LOG("find process_type:%s ,k:%d", result_type.c_str(), k);
                //特殊冲突处理逻辑在此
                //1.豆瓣影视 多实体 以 上映日期排序 取最新的一个
                //(只能处理两部都是电影/电视剧 不能处理1电影1电视剧情况)
                //因为schema建设不符合规范 regionalReleaseDate premiereDate都叫上映时间
                if (element[k].isMember(search_property) && element[k][search_property].isArray()){
                    //旅游类统一采用热度择优,不做属性区分
                    if(result_type=="Scene" )
                    {
                        int cur_hot=0;
                        if(element[k].isMember("viewCount") && element[k]["viewCount"].isArray())//有热度信息
                        {
                std::string hot_string=element[k]["viewCount"][(size_t)0].asString();
                cur_hot=atoi(hot_string.c_str());
                        }
                        else //无热度信息,默认热度是1
                        {
                            cur_hot=1;
                        }
            CNOTICE_LOG("k: %d cur hot:%d",k, cur_hot);
                        //排序
                        if(cur_hot >= scene_hot)
                        {
                            scene_hot=cur_hot;
                            process_loc=k;
                CNOTICE_LOG("final process_type:%s k:%d hot:%d", result_type.c_str(), k, cur_hot);
                        }
                    }
                    //如果查询属性属于影视类 则需要判断逻辑 取最新的电影
                    else if ((search_property == "score" || search_property == "regionalReleaseDate")
                            || element[k].isMember("regionalReleaseDate")){
                        for (size_t i = 0; i < element[k]["regionalReleaseDate"].size(); i++){
                            std::string local_date = element[k]["regionalReleaseDate"][i].asString();
                            std::string year_temp_str = "1893";
                            std::string month_temp_str = "12";
                            //数据有 regionalReleaseDate = 2015 形式 因此需判断日期长度 从而截取年月
                            if (local_date.length() >= 4){
                                year_temp_str = local_date.substr(0, 4);
                            }
                            if (local_date.length() >= 7){
                                month_temp_str = local_date.substr(5, 2);
                            }
                            int year_temp = string_to_int(year_temp_str);
                            int month_temp = string_to_int(month_temp_str);
                            if (year_temp > year || (year_temp == year && month_temp > month)){
                                process_loc = k;
                                year = year_temp;
                                month = month_temp;
                                CNOTICE_LOG("final process_type:%s k:%d", result_type.c_str(), k);
                                CNOTICE_LOG("find date %s is later,query %s,location:%d",
                                        local_date.c_str(), fifadata_handle->src_query.c_str(), k);
                            }
                        }
                    }
                    else{
                        //非电影类 同一类别出多个结果 随机出1个
                        process_loc = k;
                        CNOTICE_LOG("final process_type:%s k:%d", result_type.c_str(), k);
                        break;
                    }
                } else if (search_property=="" &&
                        fifadata_handle->spo_query.find("out") != std::string::npos){
                    //山东省会 此类纯边查询 处理逻辑
                    std::string spo_query_src = fifadata_handle->spo_query;
                    int spo_query_len = spo_query_src.size();
                    if (spo_query_src.substr(spo_query_len - 10, 10) != ".with(\'*\')") {
                        CWARNING_LOG("spo_query : \"%s\" is not end with \".with(\'*\')\".",
                                fifadata_handle->spo_query.c_str());
                        return -1;
                    }
                    int j = spo_query_len - 10;
                    for (j = spo_query_len - 10; j >= 0; --j) {
                        if (spo_query_src.substr(j, 4) == ".out") {
                            //得到边的英文：.out("edgename").with('*')
                            search_edge = spo_query_src.substr(j + 6, spo_query_len - 10 - j - 8);
                            CNOTICE_LOG("find edge %s", search_edge.c_str());
                            break;
                        }
                    }
                    CNOTICE_LOG("info %s,%d,%d", spo_query_src.c_str(),
                            spo_query_src.length(), spo_query_src.find("out"));
                    int local_start = spo_query_src.find("has(\'name\',MATCH");
                    CNOTICE_LOG("local_start %d", local_start);
                    std::string midd_gremlin;
                    //midd_gremlin = ('name',MATCH,'中国')
                    //local_start + 3 means length(has)
                    if (local_start != std::string::npos){
                        midd_gremlin = spo_query_src.substr(local_start + 3,
                                spo_query_src.find(".out") - local_start -3);
                    }
                    //std::string midd_gremlin = spo_query_src.substr(spo_query_src.find_last_of("has")+3,
                    //        spo_query_src.find("out")-30);
                    CNOTICE_LOG("middle_gremlin %s", midd_gremlin.c_str());
                    if (midd_gremlin.substr(0, 14) == "(\'name\',MATCH,"){
                        title_name = midd_gremlin.substr(15, midd_gremlin.length()-17);
                        CNOTICE_LOG("match_here");
                        process_loc = k;
                    }else{
                        CWARNING_LOG("name_da gremlin error");
                        return -1;
                    }
                } else{
                    CNOTICE_LOG("location %d dont have prop %s", k, search_property.c_str());
                }
            }else{
                CNOTICE_LOG("return data type %s\t,but dont process", result_type.c_str());
            }
        }
    }
    if (process_loc == -1){
        CNOTICE_LOG("query %s dont process", fifadata_handle->src_query.c_str());
        return -1;
    }
    CNOTICE_LOG("final process_location:%d", process_loc);
    //此处已经决定最优实体为process_loc 不需要for循环
//    for(size_t k = process_loc; k < element.size(); ++k){
        size_t k = process_loc;
        EntityBodyPtr entity = ::sofa::create< EntityBody >();
        faci::graphsearch::Json& s_entity = element[k];
        if (s_entity.isMember("type") && s_entity["type"].isArray() && s_entity["type"].size()>0 && s_entity["type"][(size_t)0].isString()){
            result_type = s_entity["type"][(size_t)0].asString();
            CNOTICE_LOG("final process_type is %s", result_type.c_str());
        }
        if (s_entity.isMember("name") && s_entity["name"].isArray() && s_entity["name"].size()>0 && s_entity["name"][(size_t)0].isString()){
            name = s_entity["name"][(size_t)0].asString();
        } else{
            CFATAL_LOG("result do not include name");
            return -4;
        }
        faci::graphsearch::Json::Members mems = s_entity.getMemberNames();
        for (faci::graphsearch::Json::Members::iterator iter = mems.begin(); iter != mems.end(); ++iter) {
            if (s_entity[*iter].isArray()) {
                std::string new_value;
                int tag = 0;
                //summaryImgSingle 字段有多值 取第一个即可。
                if (*iter == "summaryImgSingle" && s_entity[*iter].size()>0 && s_entity[*iter][(size_t)0].isString()){
                    new_value = s_entity[*iter][(size_t)0].asString();
                    s_entity[*iter] = new_value;
                    CDEBUG_LOG("summaryImgSingle is :%s\t", new_value.c_str());
                    continue;
                }
                //guide和wise_guide是旅游数据wsie和pc不同的落地页,归一到url
                if( *iter=="guide" && s_entity[*iter].size()>0 && s_entity[*iter][(size_t)0].isString())
                {
                    if( fifadata_handle->client_name=="us"||fifadata_handle->client_name=="")
                    {
                        new_value = s_entity[*iter][(size_t)0].asString();
                        s_entity["url"]=new_value;
            jump_url=new_value;
                        CDEBUG_LOG("url replace by guide:%s\t", new_value.c_str());
                    }
                }
                if( *iter=="wiseGuide" && s_entity[*iter].size()>0 && s_entity[*iter][(size_t)0].isString())
                {
                    if( fifadata_handle->client_name=="wise-us")
                    {
                        new_value = s_entity[*iter][(size_t)0].asString();
                        s_entity["url"]=new_value;
            jump_url=new_value;
                        CDEBUG_LOG("url replace by wiseGuide:%s\t", new_value.c_str());
                    }
                }


                //保存下 旅游类数据的url字段 作为左侧图片的跳转链接
                if ((*iter)=="url" && s_entity[*iter].isArray() && s_entity[*iter].size()>0  && s_entity[*iter][(size_t)0].isString()){
                    jump_url = s_entity[*iter][(size_t)0].asString();
                    CDEBUG_LOG("jump-url is :%s\t", name.c_str());
                }
                //检测查询属性 如果属性的值为空，不展现
                if ((*iter) == search_property && s_entity[*iter].size()>0  && s_entity[*iter][(size_t)0].isString()){
                    if (s_entity[*iter][(size_t)0].asString() == ""){
                        CWARNING_LOG("entity has property but value is null,name type searchp is %s\t%s\t", name.c_str(), result_type.c_str(), search_property.c_str());
                        return -3;
                    }
                }
                //保存下 实体属性 searchp_chn字段需要
                if ((*iter)=="name" && s_entity[*iter].size()>0 && s_entity[*iter][(size_t)0].isString()){
                    name = s_entity[*iter][(size_t)0].asString();
                    CNOTICE_LOG("entity name is :%s\t", name.c_str());
                }
                //把数组换成string
                for (size_t pos = 0; pos != s_entity[*iter].size()-1; ++pos) {
                    if (s_entity[*iter][pos].isString()){
                        new_value += s_entity[*iter][pos].asString()+",";
                    }
                }
                //同上
                if (s_entity[*iter].size() >=1 && s_entity[*iter][s_entity[*iter].size()-1].isString()) {
                    new_value += s_entity[*iter][s_entity[*iter].size()-1].asString();
                    CDEBUG_LOG("final_new_value is :%s\t", new_value.c_str());
                }
                //上市日期逻辑：如果多日期，添加地域属性；如果只有中国大陆，不显示地域
                if (*iter == "regionalReleaseDate"){
                    std::vector<std::string> split_result;
                    int len = split_words(new_value, ",", &split_result);
                    len = split_result.size();
                    std::string str = "中国大陆" ;
                    CDEBUG_LOG("regionalReleaseDate  is :%s\t",new_value.c_str());
                    //数据内容变化 不需要此处拼接逻辑
                    /*for (int i =0; i<len; i++){
                        if (split_result[i].find(str)!=std::string::npos){
                            new_value = split_result[i].substr(0 , (split_result[i].size()-str.size()-2));
                            tag = 1;
                            break ;
                        }
                    }
                    if (tag == 0){
                        new_value = split_result[0];
                        CDEBUG_LOG("after_process regionalReleaseDate  is :%s\t",new_value.c_str());
                        }*/
                }

                //剧情简介逻辑：添加剧情简介 显示
                if (*iter == "description" && result_type == "Movie"){
                    new_value = "剧情简介:" + new_value ;
                    CDEBUG_LOG("after_process description  is :%s\t",new_value.c_str());
                }
                //fromUrl 多个@FROM_URL 取第一个
                if (*iter == "@FROM_URL"){
                    std::vector<std::string> split_result;
                    split_words(new_value, ",", &split_result);
                    new_value = split_result[0] ;
                    CDEBUG_LOG("fromurl is :%s\t",new_value.c_str());
                }
                s_entity[*iter] = new_value;
            }
        }
        s_entity.toString(tmp_result);
        CDEBUG_LOG("search result_after\t%s", tmp_result.c_str());
        if (s_entity.isMember("_id") && (s_entity["_id"].isUInt())){
            entity->set_entity_id(s_entity["_id"].asUInt64());
        }
        entity->set_entity(s_entity.toSofaObject().get());
        result->push_back(entity);
        CDEBUG_LOG("push_back_entity");


    faci::knowledge::dconfig_t display_config;

    display_config.sid = "28215";
    display_config.field = "人物";
    display_config.display_type = "single-entity";
    display_config.show_pic = "Yes";
    display_config.pic_size = "pic_6n_121";
    display_config.is_click = "Yes";
    display_config.main_keyword = "name";
    display_config.additional = "name";
    display_config.show_summary = "Yes";
    //判断当前类型result_type是否为该处理的类型
    std::vector<std::string>::iterator s =find(typelist_vector.begin(),typelist_vector.end(),result_type);
    if (s!= typelist_vector.end()){
        CNOTICE_LOG("find process_type:%s\t",result_type.c_str());
        std::map<std::string,std::string>&mapping = map_all[result_type];
        std::map<int,std::string>&mapping_conf = mapconf_all[result_type];
        std::map<std::string,std::string>&mappingedge = mapedge_all[result_type];
        if (search_property == "") {
            //判断当前查询边不在配置中,返回
            if (mappingedge.find(search_edge) != mappingedge.end()) {
                display_config.is_have_edge = "1";
                display_config.title_add_name = title_name;
                display_config.searchp = mappingedge[search_edge];
                CDEBUG_LOG("edge title = \"%s%s\"",title_name.c_str(),display_config.searchp.c_str());
            }else {
                CDEBUG_LOG("edge not in conf,return -1. edge is %s",search_property.c_str());
                return -1;
            }
        }else {
            //判断当前查询属性不在配置中,返回
            if (mapping.find(search_property)!=mapping.end()) {
                if(result_type=="Plant"){
                display_config.searchp = "的"+mapping[fifadata_handle->search_prop];
                }else{
                display_config.searchp = mapping[fifadata_handle->search_prop];}
            }else {
                CDEBUG_LOG("property not in conf,return -1.property is %s",search_property.c_str());
                return -1;
            }
        }
        display_config.pic_url = mapping_conf[0];
        display_config.sourcename = mapping_conf[1];
        display_config.summary = mapping_conf[2];
        display_config.sourcelink = mapping_conf[3];
        display_config.summary_url = mapping_conf[4];
        if (result_type == "Scene"){
            //百度旅游数据单独分资源号,跳转到旅游页面,不填jumpquery
            display_config.sid = "28218";
            display_config.jumplink = jump_url;
            CDEBUG_LOG("jumplink assignment ok,%s\t",jump_url.c_str());
        }
        if (result_type !="Scene"){
            //非百度旅游数据，需要拼接jumpquery
            display_config.jumpquery = "name";
        }
        if (result_type == "Plant"){
            display_config.sid = "28278";
        }
    }
    else{
        return -1;
    }

    char srcid_tmp[10];
    std::string srcid_str;
    snprintf(srcid_tmp, 9, "%d", fifadata_handle->srcid);
    srcid_str = srcid_tmp;
    if(display_config.sid != srcid_str) {
        CWARNING_LOG("srcid not match %d %s", fifadata_handle->srcid, fifadata_handle->src_query.c_str());
        return -1;
    }
    display_config.src_query = fifadata_handle->src_query;
    display_config.search_prop = fifadata_handle->search_prop;
    CNOTICE_LOG("ytx searchp search_prop \t%s\t%s", display_config.searchp.c_str(),display_config.search_prop.c_str());
    CDEBUG_LOG("fifadata_handle->client_name : %s", fifadata_handle->client_name.c_str());
    int ret = display_handle.outputProcess(display_config,
            *result,
            response,
            fifadata_handle->client_name);
    CDEBUG_LOG("display__ytx\t%s", (*response).c_str());
    if (ret != 0){
        CDEBUG_LOG("display return error,return number %d",ret);
        return -4;
    }

    //转度秘模板
    //先还原真实client
    if (fifadata_handle->client_name_real!="")
    {
        fifadata_handle->client_name = fifadata_handle->client_name_real;
    }   
    if (fifadata_handle->client_name == "dumi" || fifadata_handle->client_name == "du_aries")
    {
        std::string new_response;
        if (0!=trans_dumi(fifadata_handle, *response, new_response))
        {
            CDEBUG_LOG("trasn dumi failed! query=%s", fifadata_handle->src_query.c_str());
            return -1;
        }
        *response = new_response;
        kg_res->push_back(card);
        return 0;
    }
    //旅游产品时间与票价计算
    if (result_type == "Scene") {
        if (fifadata_handle->client_name=="us" || fifadata_handle->client_name=="") {
            ::faci::graphsearch::Json scene_json;
            std::string response_str = *response;
            CDEBUG_LOG("compute start %s",response_str);
            //scene_json.fromString(response_str);
            CDEBUG_LOG("compute start %s",response_str);

            //compute_scene_pc(scene_json);

            //scene_json.toString(response_str);
            //*response = response_str;
        }
    }

    kg_res->push_back(card);
    return 0;

}

bool MoviePluginImp::check_holiday(std::string holiday) {
    //::sofa::ObjectPtr __ret;
    //::sofa::ObjectPtr extra_info;
    //std::string spo_query = "date_delta(today(), date_from_string(\""+holiday+"\"), \"Year\")";
    //int req = gremlinConnect->computeQuery(spo_query, __ret, extra_info, _s_sa_resource_name);
    //CDEBUG_LOG("sa_spo : %d", req);
    //CDEBUG_LOG("spo_query : %s", spo_query.c_str());
    //faci::graphsearch::Json json_age(__ret);
    return false;
}

std::string MoviePluginImp::compute_today_openinghours(::faci::graphsearch::Json structured_json) {
    ::faci::graphsearch::Json result = structured_json["openingHours"];
    std::string opentime="";
    std::string closetime="";
    CDEBUG_LOG("compute_today_openinghours input: %s", result.asString());
    if ( !result.isArray() )
    {
        CDEBUG_LOG("result is not array");
        return NULL;
    }
    for( size_t i=0; i<result.size(); i++ )
    {
        ::faci::graphsearch::Json tmp = result[i];
        bool check_month = false;
        bool check_week = false;
        bool has_month = false;
        bool has_week = false;
        if ( tmp.isMember("month") ) {
            has_month = true;
            if ( tmp["month"].isMember("info") ) {
                if (check_holiday(tmp["month"]["info"].asString())) {
                    check_month = true;
                }
            }
            if (tmp["month"].isMember("start") && tmp["month"]["start"].asString()!="0000") {
                if (check_holiday(tmp["month"]["start"].asString()+"~"+tmp["month"]["end"].asString())) {
                    check_month = true;
                }else {
                    check_month = false;
                }
            }
        }
        if (has_month&&check_month){
            if (tmp.isMember("week")) {
                has_week = true;
                if (tmp["week"].isMember("start")) {
                    if (check_holiday(tmp["week"]["start"].asString()+"~"+tmp["week"]["end"].asString())) {
                        check_week=true;
                    }else {
                        check_week=false;
                    }
                }
            }
        }
        
        if ((has_month&&check_month)&&(has_week&&check_week)) {
            opentime = tmp["hour"]["opentime"].asString();
            closetime = tmp["hour"]["closetime"].asString();
        }
    }

    if (!structured_json.isMember("specialHours")) {
        return opentime + "~" + closetime;
    }
    result = structured_json["specialHours"];
    CDEBUG_LOG("compute_today_openinghours input: %s", result.asString());
    if ( !result.isArray() )
    {
        CDEBUG_LOG("result is not array");
        return NULL;
    }
    bool week_close = false;
    for( size_t i=0; i<result.size(); i++ )
    {
        ::faci::graphsearch::Json tmp = result[i];
        if (tmp.isMember("holiday")) {
            if (tmp["type"].asString()=="close") {
                for( size_t j=0; j<tmp["holiday"].size(); j++ ) {
                    if (check_holiday(tmp["holiday"][j].asString())) {
                        if (tmp["holiday"][j].asString().find_first_of("周", 0)==-1){
                            return "close";
                        }else {
                            week_close = true;
                        }
                    }
                }
            }else {
                for( size_t j=0; j<tmp["holiday"].size(); j++ ) {
                    if (check_holiday(tmp["holiday"][j].asString())) {
                        if (tmp.isMember("hour")) {
                            if (tmp["hour"].isMember("opentime")) {
                                opentime = tmp["hour"]["opentime"].asString();
                            }
                            if (tmp["hour"].isMember("closetime")) {
                                closetime = tmp["hour"]["closetime"].asString();
                            }
                        }
                        return opentime + "~" + closetime;
                    }
                }
            }
        }
    }
    if (week_close) {
        return "close";
    }
    return opentime + "~" + closetime;
}

std::string MoviePluginImp::compute_today_price(::faci::graphsearch::Json structured_json) {
    ::faci::graphsearch::Json result = structured_json;
    CDEBUG_LOG("compute_today_price input: %s", result.asString());
    if ( !result.isArray() )
    {
        CDEBUG_LOG("result is not array");
        return NULL;
    }
    for( size_t i=0; i<result.size(); i++ )
    {
        ::faci::graphsearch::Json tmp = result[i];
        if (tmp.isMember("month")) {
            if (tmp["month"].isMember("start")) {
                if (check_holiday(tmp["month"]["start"].asString()+"~"+tmp["month"]["end"].asString())) {
                    return tmp["price"].asString();
                }
            }else if(tmp["month"].isMember("info")) {
                if (check_holiday(tmp["month"]["info"].asString())) {
                    return tmp["price"].asString();
                }
            }
        }else {
                return tmp["price"].asString();
        }
    }
    CDEBUG_LOG("None Price");
    return NULL;
}

void MoviePluginImp::compute_scene_pc(::faci::graphsearch::Json& scene_json) {
    if (!scene_json.isNull() && scene_json.isMember("structured_info")) {
        CDEBUG_LOG("compute_scene_pc input: %s", scene_json.asString());
        std::string structured_info = scene_json["structured_info"].asString();
        ::faci::graphsearch::Json structured_json;
        structured_json.fromString(structured_info);

        // 计算当天时间和票价
        if (structured_json.isMember("openingHours")) {
            scene_json["todayOpeningHours"] = compute_today_openinghours(structured_json);
        }
        if (structured_json.isMember("price")) {
            scene_json["todayPrice"] = compute_today_price(structured_json["price"]);
        }
        // 提取带换行的详细时间与票价
        if (structured_json.isMember("detail_openingHours")) {
            scene_json["detailOpeningHours"] = structured_json["detail_openingHours"].asString();
        }
        if (structured_json.isMember("detail_price")) {
            scene_json["detailPrice"] = structured_json["detail_price"].asString();
        }
    }
}

void MoviePluginImp::async_DoQuery(
        ::sofa::AsyncControllerPtr __cntl,int64_t* __ret,uint64_t handle,
        ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr >* result,
        ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr >* response){
    typedef int64_t __ret_type;
    SOFA_ASYNC_TO_SYNC(__ret_type, DoQuery, handle, result, response);}

int64_t MoviePluginImp::QueryDone(
        uint64_t handle)
{
    // TODO: add implement code here.
    // blank this
    //SOFA_THROW(::sofa::NotImplementException, "MoviePluginImp::QueryDone");


    //struct SPOThreadFifaData_t* fifadata_handle = (struct SPOThreadFifaData_t*)handle;
    //fifadata_handle->src_query = "";
    //fifadata_handle->spo_query = "";
    //fifadata_handle->search_prop = "";
    return 0;
}

int MoviePluginImp::trans_dumi(const SPOThreadFifaData_t* params, const std::string& input, std::string& output)
{
    /* {error: 0(-1), "origin_query": "xxxxx", "norm_query": "xxxxx", "result_list": [{"title": "", "abstract": "", "url": "", "img": ""}, {"title": "", “ abstract": "", "url": "", "img": ""}], score: 120} */
    ::faci::graphsearch::Json input_json;
    ::faci::graphsearch::Json output_json;
    ::faci::graphsearch::Json result_list;
    CDEBUG_LOG("trans_dumi input: %s", input.c_str());
    CDEBUG_LOG("trans_dumi src_query: %s", params->src_query.c_str());
    input_json.fromString(input);

    //目前只需要处理exactqa和ks_general两种模板即可
    if ( input_json.isMember("resultData") && input_json["resultData"].isMember("tplData") && input_json["resultData"]["tplData"].isMember("result") ) //是exactqa
    {
        ::faci::graphsearch::Json result = input_json["resultData"]["tplData"]["result"];
        if ( !result.isArray() )
        {
            CDEBUG_LOG("result is not array");
            return -1;
        }
        //确定主答案区域
        std::vector<std::string> ans;
        if (input_json["resultData"]["tplData"].isMember("search_property"))
        {
            //可能有多属性按|切割
            std::string tmp = input_json["resultData"]["tplData"]["search_property"].asString();
            boost::split(ans, tmp, boost::is_any_of("|"));
        }
        else
        {
            ans.push_back("ename");
        }
        //确定title
        std::string title;
        if (input_json["resultData"]["tplData"].isMember("search_property"))
        {
            title = input_json["resultData"]["tplData"]["display_title"].asString();
        }
        else
        {
            title = params->src_query;
        }

        

        //多答案压缩到一个卡片
        //title
        result_list[(size_t)0]["title"] = title;
        //多答案url直接发起搜索,无img
        if (result.size()>1)
        {
            result_list[(size_t)0]["url"] = "http://www.baidu.com/s?wd=" + params->src_query;
        }
        else //单答案还是照样填url,img
        {
            ::faci::graphsearch::Json tmp = result[(size_t)0];
            //填写图片,优先选大的
            if (tmp.isMember("pic_6n_121") && tmp["pic_6n_121"].asString().size()!=0)
            {
                result_list[(size_t)0]["img"] = tmp["pic_6n_121"].asString();
            }
            if (tmp.isMember("pic_4n_78") && tmp["pic_4n_78"].asString().size()!=0)
            {
                result_list[(size_t)0]["img"] = tmp["pic_4n_78"].asString();
            }
            //填写落地页
            if (tmp.isMember("sourcelink") && tmp["sourcelink"].asString().size()!=0 )
            {
                result_list[(size_t)0]["url"] = tmp["sourcelink"].asString();
            }
        }
        //文本答案压缩
        for( size_t i=0; i<result.size(); i++ )
        {
            ::faci::graphsearch::Json tmp = result[i];
            std::string merged_ans;
            //填写文本区abstract,多结果的拼一起
            for (size_t i=0; i<ans.size(); i++)
            {
                if (tmp.isMember(ans[i]) && tmp[ans[i]].asString().size()!=0 )
                {
                    merged_ans += tmp[ans[i]].asString()+"\n";
                }
                else
                {
                    //没文本答案算错误
                    CDEBUG_LOG("result has not main-answer-field:%s", ans[i].c_str());
                    return -1;
                }
            }
            result_list[(size_t)0]["abstract"] = merged_ans;
        }
    }
    else if ( input_json.isMember("answer") ) //是ks_general
    {
        //title,公用的
        std::string title;
        if ( input_json.isMember("answertitle") && input_json["answertitle"].asString().size()!=0 )
        {
            title = input_json["answertitle"].asString();
        }
        else
        {
            title = params->src_query;
        }
        //主答案
        if ( input_json.isMember("answer") && input_json["answer"].isArray() )
        {
            

            //多答案压缩到一个卡片
            //title
            result_list[(size_t)0]["title"] = title;
            //url
            if (input_json.isMember("url") && input_json["url"].asString().size()!=0)
            {
                result_list[(size_t)0]["url"] = input_json["url"].asString();
            }
            else
            {
                result_list[(size_t)0]["url"] = "http://www.baidu.com/s?wd=" + params->src_query;
            }
            //img
            if (input_json["answer"].size()==1)
            {
                ::faci::graphsearch::Json tmp = input_json["answer"][(size_t)0];
                if (tmp.isMember("img") && tmp["img"].asString().size()!=0 )
                {
                    result_list[(size_t)0]["img"] = tmp["img"].asString();
                }
            }
            //文本答案压缩
            std::string merged_abstract;
            for (size_t i=0; i<input_json["answer"].size(); i++)
            {
                ::faci::graphsearch::Json tmp = input_json["answer"][i];
                if (tmp.isMember("ename") && tmp["ename"].asString().size()!=0 )
                {
                    merged_abstract += tmp["ename"].asString() + "\n";
                }
            }
             result_list[(size_t)0]["abstract"] = merged_abstract;

        }
        else
        {
             CDEBUG_LOG("ks_general has not answer-field");
             return -1;
        }
    }
    else //不认识的模板
    {
        CDEBUG_LOG("unkown kv template");
        return -1;
    }
    //填写output模板固定的部分
    output_json["origin_query"] = params->src_query;
    output_json["norm_query"] = params->norm_query; //后面要改成request里一致的
    output_json["score"] = 100;
    output_json["error"] = 0; 
    output_json["result_list"] = result_list;

    output_json.toString(output);

    return 0;
}

void MoviePluginImp::async_QueryDone(
        ::sofa::AsyncControllerPtr __cntl,int64_t* __ret,uint64_t handle){
    typedef int64_t __ret_type;
    SOFA_ASYNC_TO_SYNC(__ret_type, QueryDone, handle);}

SOFA_REGISTER_SERVICE_IMPLEMENT("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp", MoviePluginImp);
//SOFA_REGISTER_SERVICE_LINK("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp", "com.baidu.wd.knowledge.ver_1_0_0.KgPlugin", "demospo");

} // namespace ver_1_0_0
} // namespace knowledge
} // namespace wd
} // namespace baidu
} // namespace com
} // namespace imp

/* vim: set ts=4 sw=4 sts=4 tw=100 */
