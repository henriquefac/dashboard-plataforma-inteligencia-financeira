import streamlit as st
import pandas as pd

from app.api.v1.client import client
from app.models import FilterParams, RangeFilter, FilterMeta, FiltersResponse

class FilterSidebar:
    def __init__(self):
        # filtros disponíveis
        self.filter_meta: FiltersResponse = None
        self.filter_params: FilterParams = None
    def render(self):
        # pegar request do cliente
        if not client.ingest_id:
            return
        
        if not self.filter_meta:
            self.filter_meta = client.get_filters()
            self.filter_params = FilterParams(root={})
                
        # agora que possui os metadados, pode comerçar a construir o painel lateral.
        st.sidebar.header("Filtros")
        
        for f in self.filter_meta.filters:
            if f.filter_type == "range":
                self.build_range_filter_sidebar(f)
            elif f.filter_type == "tag":
                self.build_tag_filter_sidebar(f)

    def build_range_filter_sidebar(self, filter: FilterMeta):
        if filter.kind == "date":
            filter.min = pd.to_datetime(filter.min).date()
            filter.max = pd.to_datetime(filter.max).date()
            date_range = st.sidebar.date_input(filter.column_name, value=(filter.min, filter.max))

            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                self.filter_params.root[filter.column] = RangeFilter(min=date_range[0].isoformat(), max=date_range[1].isoformat())
        else:
            slider_range = st.sidebar.slider(filter.column_name, filter.min, filter.max, (filter.min, filter.max))

            if isinstance(slider_range, (list, tuple)) and len(slider_range) == 2:
                self.filter_params.root[filter.column] = RangeFilter(min=slider_range[0], max=slider_range[1])

    def build_tag_filter_sidebar(self, filter: FilterMeta):
        val = st.sidebar.multiselect(filter.column_name, options=filter.values, default=filter.values)
        if len(val) > 0:
            self.filter_params.root[filter.column] = val
        else:
            self.filter_params.root[filter.column] = None