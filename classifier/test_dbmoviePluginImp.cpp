/***************************************************************************
 *
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 *
 **************************************************************************/

#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <gtest/gtest.h>
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
#include <sofa/kernel/implements.h>
#include <sofa/kernel/runtime.h>
#include <GremlinServerConnect.h>
#include <com/baidu/wd/knowledge/ver_1_0_0.h>
#include <com/baidu/wd/knowledge/da/ver_1_0_0.h>
#include <KGDAServerConnect.h>
#include <ServiceApiServerConnect.h>
#include "json/json.h"
#include "JsonObj.h"
#include "QueryObject.h"
#include "test_MoviePluginImp.h"
using namespace ::com::baidu::wd::knowledge::ver_1_0_0;
using namespace ::com::baidu::wd::knowledge::da::ver_1_0_0;
using namespace ::faci::knowledge;
using namespace ::movie_plugin::btest;
using namespace std;

//存储单测的query列表，供TEST_P使用
vector<string> g_query_list;

//存储kgda的client
KGDAServerConnect* kgdaConnect;

int main(int argc, char **argv)
{
    ::sofa::Config configs;
    configs["sofa.runtime.sidb"] = "embedded://../../sidb/";
    configs["sofa.runtime.dlclose_on_unload"] = "false";
    ::sofa::init(configs);
    ::sofa::Config kg_server_conf;
    int ret = kg_server_conf.load("./conf/kg-server.xml");
    if (0 == ret){
        std::cerr << "./conf/kg-server.xml load error" << std::endl;
        return -1;
    }
    // ret = GremlinServerConnect::setConn(kg_server_conf["kg-server"]["gremlin"]);
    ret = ServiceApiServerConnect::setConn(kg_server_conf["kg-server"]["kgopen"]);
    if (0 != ret){
        std::cerr << "ServiceApiServerConnect::setConn failed" << std::endl;
        return -1;
    }

    //加载query列表
    ifstream query_file("./conf/query_list");
    if (query_file){
        string line;
        while (getline(query_file, line)){
            g_query_list.push_back(line);
        }
    }else {
        std::cerr << "./conf/quer_list none" << std::endl;
    }

    kgdaConnect = new KGDAServerConnect();
    if (kgdaConnect->init(kg_server_conf["kg-server"]["kgda"]) != 0){
        delete kgdaConnect;
        std::cerr << "kgda connect init failed" << std::endl;
        return -1;
    }

 	testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

/**
 * @brief
**/
class test_KgPluginPersonImp_suite : public ::testing::TestWithParam<string>{
    protected:
        test_KgPluginPersonImp_suite(){};
        virtual ~test_KgPluginPersonImp_suite(){};
        virtual void SetUp()
        {
            //Called befor every TEST_F(test_KgPluginPersonImp_suite, *)
        };
        virtual void TearDown()
        {
            //Called after every TEST_F(test_KgPluginPersonImp_suite, *)
        };
};

INSTANTIATE_TEST_CASE_P(AnotherInstantiationName, test_KgPluginPersonImp_suite, ::testing::ValuesIn(g_query_list));

/**
 * @brief
 * @begin_version
**/
TEST_P(test_KgPluginPersonImp_suite, test_QueryStream__1)
{
	//TODO
    string query = GetParam();
    cout << "TEST_P src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28215);
    //KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.KgPluginPersonImp");
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    //std::string conf_path = "./conf/spo-person.xml";
    std::string conf_path = "./conf/movie.xml";
    int ret = kg_plugin->InitOnce(conf_path);
    ASSERT_EQ(0, ret);
    ret = kg_plugin->reload();

    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t __ret;
    kg_plugin->async_reload(controller, &__ret);



    ASSERT_EQ(0, ret);

    uint64_t handle;
    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('name',MATCH,'失孤').with('*')#score\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    ret = kg_plugin->DoQuery(handle, &result, &response);
    EXPECT_EQ(0, ret);

    kg_plugin->QueryDone(handle);
    /*
    query_param->set_srcid(28215);
    int ret2 = kg_plugin->InitOnce(conf_path);
    ASSERT_EQ(0, ret2);
    ret2 = kg_plugin->reload();
    ::sofa::AsyncControllerPtr controller2 = ::sofa::new_async_controller();
    controller2->set_timeout(500);
    int64_t __ret2;
    kg_plugin->async_reload(controller2, &__ret2);
    ASSERT_EQ(0, ret2);
    uint64_t handle2;
    ret2 = kg_plugin->AcceptQuery(query_param, &handle2);
    ASSERT_EQ(0, ret2);
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result2;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response2;
    ret2 = kg_plugin->DoQuery(handle2, &result2, &response2);
    EXPECT_EQ(-1, ret2);
    kg_plugin->QueryDone(handle2);
    */
}




/**
 * @brief:添加异常参数的测试案例，增加单测覆盖率
 **/
class test_KgPluginPersonImp_AsyncFunctions_suite : public testing::Test
{
/*    public:
        virtual void SetUp(){};
        virtual void TearDown(){};
*/
};

/**
 * @brief: 调用异步接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_AsyncFunctions_suite, testCase1)
{

    string query = g_query_list[0];
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28215);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('name',MATCH,'失孤').with('*')#score\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);

    }


TEST_F(test_KgPluginPersonImp_AsyncFunctions_suite, testCase2)
{

    string query = "西湖门票";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);
    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/leizhouxihu').with('*')#address\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);

}

class test_KgPluginPersonImp_InitOnce_suite : public testing::Test
{
    public:
        virtual void SetUp(){};
        virtual void TearDown(){};
};


TEST_F(test_KgPluginPersonImp_InitOnce_suite, testCase1)
{
        KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
        std::string conf_path = "./conf/movie.xml";
        int64_t ret = kg_plugin->InitOnce(conf_path);
        EXPECT_EQ(0, ret);
}

/* vim: set expandtab ts=4 sw=4 sts=4 tw=100: */


/**
 * @brief:添加旅游结构化的测试案例，增加单测覆盖率
 **/
class test_KgPluginPersonImp_Structured_suite : public testing::Test
{
/*    public:
        virtual void SetUp(){};
        virtual void TearDown(){};
*/
};

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase1)
{
    string query = "798艺术区开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/798yishuqu').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"798艺术区开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);
    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase2)
{
    string query = "故宫开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"故宫开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase3)
{
    string query = "黄鹤楼开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/huanghelou').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"黄鹤楼开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase4)
{
    string query = "深圳欢乐谷开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/shenzhenhuanlegu').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"深圳欢乐谷开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase5)
{
    string query = "趵突泉开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/baotuquan').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"趵突泉开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase6)
{
    string query = "东西连岛开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/dongxiliandao').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"东西连岛开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }

/**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase7)
{
    string query = "中国科学技术馆开放时间";
    cout << "src query is: " << query << endl;
    ::sofa::vector<da_resultPtr> da_results;
    kgdaConnect->daQuery(query, da_results);
    ASSERT_NE((unsigned)0, da_results.size());
    QueryParamPtr query_param = ::sofa::create<QueryParam>();
    query_param->set_da_extra(da_results[0]->extra_des());
    query_param->set_da_query(da_results[0]->res_query());
    query_param->set_text_query(da_results[0]->src_query());
    query_param->set_srcid(28218);
    KgPluginPtr kg_plugin = ::sofa::create<KgPlugin>("imp.com.baidu.wd.knowledge.ver_1_0_0.MoviePluginImp");
    std::string conf_path = "./conf/movie.xml";
    ::sofa::AsyncControllerPtr controller = ::sofa::new_async_controller();
    controller->set_timeout(500);
    int64_t ret = kg_plugin->InitOnce(conf_path);
    controller->wait();
    ASSERT_EQ(0, ret);

    uint64_t handle;
    controller->reset();
    controller->set_timeout(500);

    query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/zhongguokexuejishuguan').with('*')#openingHours\",\"domain_type\":\"norm\",\"feature\":null,\"intent\":\"\",\"objects\":\"\",\"qp_type\":\"1\",\"query\":\"中国科学技术馆开放时间\",\"query_type\":\"None\",\"spo\":\"xxx\"}]}");
    //query_param->set_da_query("{\"result\":[{\"cmd\":\"g.has('sid',MATCH,'http://lvyou.baidu.com/gugong').with('*')#openingHours\"}]}");
    ret = kg_plugin->AcceptQuery(query_param, &handle);
    controller->wait();
    ASSERT_EQ(0, ret);

    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::EntityBodyPtr > result;
    ::sofa::vector< ::com::baidu::wd::knowledge::ver_1_0_0::KgCardPtr > response;
    controller->reset();
    controller->set_timeout(500);
    ret = kg_plugin->DoQuery(handle, &result, &response);
    controller->wait();
    EXPECT_EQ(0, ret);

    cout << "src query is: " << ret << endl;
    controller->reset();
    controller->set_timeout(500);
    kg_plugin->QueryDone(handle);
 }
std::string DoQuery(::sofa::ObjectPtr __ret)
{
    faci::graphsearch::Json element(__ret);
    std::string tmp_result;
    std::string name;
    std::string jump_url = "lvyou.baidu.com";
    std::string result_type = "Scene";
    element.toString(tmp_result);
    std::string search_edge = "";
    std::string title_name = "";
    if(element.isNull()){
        return "";
    }

        faci::graphsearch::Json& s_entity = element[(size_t)0];
        if (s_entity.isMember("type") && s_entity["type"].isArray() && s_entity["type"].size()>0 && s_entity["type"][(size_t)0].isString()){
            result_type = s_entity["type"][(size_t)0].asString();
            CDEBUG_LOG("final process_type is %s", result_type.c_str());
        }
        if (s_entity.isMember("name") && s_entity["name"].isArray() && s_entity["name"].size()>0 && s_entity["name"][(size_t)0].isString()){
            name = s_entity["name"][(size_t)0].asString();
        } else{
            CDEBUG_LOG("result do not include name");
            return "";
        }
        faci::graphsearch::Json::Members mems = s_entity.getMemberNames();
        for (faci::graphsearch::Json::Members::iterator iter = mems.begin(); iter != mems.end(); ++iter) {
            if (s_entity[*iter].isArray()) {
                std::string new_value;
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
                if (*iter == "structured_info" && s_entity[*iter].size() >=1){
                    s_entity[*iter] = s_entity[*iter][s_entity[*iter].size()-1];
                }else {
                    s_entity[*iter] = new_value;
                }
            }
		}
	    s_entity.toString(tmp_result);
	    CDEBUG_LOG("search result_after\t%s", tmp_result.c_str());
	return tmp_result;

}
 /**
 * @brief: 调用旅游结构化接口，增加函数覆盖率
 **/
TEST_F(test_KgPluginPersonImp_Structured_suite, testCase8)
{
    //ifstream fin("output.txt");
    faci::knowledge::ServiceApiServerConnect* gremlinConnect =
    faci::knowledge::ServiceApiServerConnect::getConn();
    ::faci::graphsearch::Json scene_json ;
    test_MoviePluginImp mpi ;
    std::string response_str;
    struct tm *ptm = new struct tm;
    for (int i=6; i<30; i++) {
        string query = g_query_list[i];
        string spo_query = "g.query().has('name',MATCH,'"+query+"').with('*')";
        string resource_name = "spo_lvyou";
        ::sofa::ObjectPtr __ret;
        ::sofa::ObjectPtr extra_info;
        gremlinConnect->gremlinQuery(spo_query, __ret, extra_info, resource_name);
        std::string tmp_result = DoQuery(__ret);
        //元旦
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 1-1;
        ptm->tm_mday = 1;
        ptm->tm_wday = 1;

        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
        //春节
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 2-1;
        ptm->tm_mday = 7;
        ptm->tm_wday = 0;
        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
        //清明
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 4-1;
        ptm->tm_mday = 4;
        ptm->tm_wday = 1;

        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
        //51
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 5-1;
        ptm->tm_mday = 1;
        ptm->tm_wday = 0;

        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
        //暑假
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 7-1;
        ptm->tm_mday = 31;
        ptm->tm_wday = 0;

        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
        //春节
        ptm->tm_hour = 12;
        ptm->tm_min = 0;
        ptm->tm_sec = 0;
        ptm->tm_year = 2016-1900;
        ptm->tm_mon = 9-1;
        ptm->tm_mday = 15;
        ptm->tm_wday = 4;

        //旅游产品时间与票价计算
        CDEBUG_LOG("compute_scene_pc start");
        response_str = tmp_result;
        scene_json.fromString(response_str);
        if (!scene_json.isNull()) {
            mpi.compute_scene_pc(ptm,scene_json);
        } else {
            CNOTICE_LOG("The json couldn't be parsed");
        }
    }
}
