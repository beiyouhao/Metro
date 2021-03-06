# App/Flow/models.py
# import from framework
from django.db import models
import datetime, traceback
import pickle
# import from project

def generate_fields():
    class AbstractModel(models.Model):
        class Meta:
            abstract = True
    for i in range(1, 32):
        AbstractModel.add_to_class('date_%s'%i, 
            models.BinaryField(blank=True)
        )
    return AbstractModel

class Flow(generate_fields()):
    id = models.IntegerField(primary_key=True)
    def __str__(self):
        return "%s" % (str(self.id))
    class Meta:
        db_table = "flow"

def __create_flow_model(db_table2):
    class MetaClass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            name += db_table2
            return models.base.ModelBase.__new__(cls, name, bases, attrs)
    class HandleClass(generate_fields()):
        __metaclass__ = MetaClass
        id = models.IntegerField(primary_key=True)

        class Meta:
            db_table = db_table2
    return HandleClass

def get_flow_db():
    from django.db import connection
    return connection.settings_dict["NAME"]

def exe_sql(sql):
    from django.db import connection
    cr = connection.cursor()
    cr.execute(sql)
    try:
        connection.commit()
    except:
        pass
    return cr

def get_flow_model(year=None, month=None):
    if year==None or month== None:
        dt = datetime.datetime.now()
        current_table_suffix = "_%s_%s" % (dt.year, dt.month)
    else:
        current_table_suffix = "_%s_%s" % (year, month)
    current_table = Flow._meta.db_table + current_table_suffix
    sql = "CREATE TABLE %s (id integer NOT NULL, "
    for i in range(1,32):
        sql = sql + "date_%s longblob NOT NULL, "%i
    sql = sql + 'PRIMARY KEY (id));'
    try:
        SQL = "SELECT count(*) AS is_exist FROM information_schema.tables WHERE table_schema = '%s' AND table_name = '%s';" % (get_flow_db(), current_table)
        cr = exe_sql(SQL)
        is_exist = cr.fetchall()[0][0]
        if not is_exist:
            print(sql % current_table)
            exe_sql(sql % current_table)
        return __create_flow_model(db_table2=current_table)
    except:
        print(traceback.print_exc())
        return Flow

def get_flow_data(year, month, dates, stations):
    FlowModel = get_flow_model(year=year, month=month)
    # 可以写成这样, 但是因为需要对每一条记录转换, 这样写还需要重新遍历字典进行转换
    # station = [], dates = []
    # return set = get_flow_model().filter(id__in=station).value_list(*dates)
    if dates == []:
        # 最简单粗暴的方法
        return {"station_%s" % s: 
                {"date_%s" % d: pickle.loads(
                    FlowModel.objects.values_list("date_%s" % d, flat=True)
                    .filter(id=s)[0]) 
                                for d in range(1, 20)} 
                                    for s in stations}
    if stations == []:
            return {"station_%s" % s: 
                {"date_%s" % d: pickle.loads(
                    FlowModel.objects.values_list("date_%s" % d, flat=True)
                    .filter(id=s)[0]) 
                                for d in dates} 
                                    for s in range(1, 82)}
    return {"station_%s" % s: 
                {"date_%s" % d: pickle.loads(
                    FlowModel.objects.values_list("date_%s" % d, flat=True)
                    .filter(id=s)[0]) 
                                for d in dates} 
                                    for s in stations}