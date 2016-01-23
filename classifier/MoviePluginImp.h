#ifndef imp__com__baidu__wd__knowledge__ver_1_0_0__MoviePluginImp
#define imp__com__baidu__wd__knowledge__ver_1_0_0__MoviePluginImp

#include <sofa/kernel/implements.h>
#include <sofa/kernel/runtime.h>
#include <com/baidu/wd/knowledge/ver_1_0_0/KgPlugin.h>
#include "json/json.h"
#include "JsonObj.h"
#include <string>
#include <GremlinServerConnect.h>
#include <ServiceApiServerConnect.h>
#include "DisplayStdstl.h"
#include <set>



namespace imp {
namespace com {
namespace baidu {
namespace wd {
namespace knowledge {
namespace ver_1_0_0 {


struct SPOThreadFifaData_t {
    std::string src_query;
    std::string spo_query;
    std::string norm_query;
    std::string search_prop;
    std::string client_name; //如果是度秘的,先转成wise的,方便走到完整的插件逻辑
    std::string client_name_real; //用于备份真正的来源
    int srcid;
    SPOThreadFifaData_t(){
    }
};


//////////////////////////////////////
//
// Implement Prototype:
//     imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp : com.baidu.wd.knowledge.ver_1_0_0.KgPlugin
//
//////////////////////////////////////
class MoviePluginImp :
    public ::sofa::implements< ::com::baidu::wd::knowledge::ver_1_0_0::KgPlugin >
{
private:
    faci::knowledge::DisplayStdstl display_handle;
    std::set< std::string > prop_list;
    std::set< std::string > searchp_list;
public:
    SOFA_DECLARE_SERVICE_IMPLEMENT(MoviePluginImp);
    MoviePluginImp();
    virtual ~MoviePluginImp();
    virtual bool init(const ::sofa::Config& conf);
public:
    // ============== methods from [com.baidu.wd.knowledge.ver_1_0_0.KgPlugin] ==============
    // InitOnce
    virtual int64_t InitOnce(
            const std::string& conf);
    virtual void async_InitOnce(
            ::sofa::AsyncControllerPtr __cntl,
            int64_t* __ret,
            const std::string& conf);
    //reload
    virtual int64_t reload();
    virtual void async_reload(
            ::sofa::AsyncControllerPtr __cntl,
            int64_t* __ret);
    // AcceptQuery
    virtual int64_t AcceptQuery(
            const ::com::baidu::wd::knowledge::ver_1_0_0::QueryParamPtr& query_param,
            uint64_t* handle);
    virtual void async_AcceptQuery(
            ::sofa::AsyncControllerPtr __cntl,
            int64_t* __ret,
            const ::com::baidu::wd::knowledge::ver_1_0_0::QueryParamPtr& query_param,
            uint64_t* handle);
    // DoQuery
    virtual int64_t DoQuery(
            uint64_t handle,
            ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr >* result,
            ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr >* kg_res);
    virtual void async_DoQuery(
            ::sofa::AsyncControllerPtr __cntl,
            int64_t* __ret,
            uint64_t handle,
            ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr >* result,
            ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr >* kg_res);
    // QueryDone
    virtual int64_t QueryDone(
            uint64_t handle);
    virtual void async_QueryDone(
            ::sofa::AsyncControllerPtr __cntl,
            int64_t* __ret,
            uint64_t handle);
    bool is_date_in_week(const struct tm *ptm, const std::string& week1, const std::string& week2);
    bool is_date_in_season(const std::string& date, const std::string& infos);
    bool is_date_in_period(const std::string& date, const std::string& date1, const std::string& date2);
    bool is_date_in_holiday(const struct tm *ptm, const std::vector<std::string>& holiday);
    std::string compute_today_price(const struct tm *ptm, ::faci::graphsearch::Json& structured_json);
    std::string compute_today_openinghours(const struct tm *ptm, ::faci::graphsearch::Json& structured_json);
    void compute_scene_pc(::faci::graphsearch::Json& scene_json);
    int trans_dumi(const SPOThreadFifaData_t* params, const std::string& input, std::string& output);
};

} // namespace ver_1_0_0
} // namespace knowledge
} // namespace wd
} // namespace baidu
} // namespace com
} // namespace imp

/* vim: set ts=4 sw=4 sts=4 tw=100 */
#endif // imp__com__baidu__wd__knowledge__ver_1_0_0__MoviePluginImp
