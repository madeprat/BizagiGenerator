#!/usr/bin/env python3
"""
Generador XPDL/BPMN Pro - S2 Grupo
Genera archivos XPDL 2.2 y BPMN 2.0 con estructura exacta de Bizagi
"""

import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Tuple


class BizagiXPDLGenerator:
    """Genera XPDL 2.2 con estructura exacta de Bizagi"""
    
    def __init__(self, process_id: str, process_name: str, country_code: str,
                 activities: List[Dict], roles: List[str]):
        self.process_id = process_id
        self.process_name = process_name
        self.country_code = country_code
        self.activities = activities
        self.roles = roles
        self.package_id = str(uuid.uuid4())
        self.process_uuid = str(uuid.uuid4())
        self.pool_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        
        # Color codes para Bizagi
        self.start_color = "-2763307"      # Verde oscuro
        self.task_color = "-1249281"        # Azul
        self.end_color = "-2763307"        # Verde oscuro
        self.border_task = "-16553830"     # Borde azul oscuro
    
    def generate(self) -> str:
        """Genera el XPDL completo"""
        
        # Crear participants
        participants = self._generate_participants()
        
        # Crear lanes
        lanes, lane_map = self._generate_lanes()
        
        # Crear activities con gráficos
        activities_xml, activity_map = self._generate_activities(lane_map)
        
        # Crear transiciones
        transitions = self._generate_transitions(activity_map)
        
        # Ensamblar XPDL
        xpdl = f'''<?xml version="1.0" encoding="utf-8"?>
<Package xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Id="{self.package_id}" Name="{self.process_id}" xmlns="http://www.wfmc.org/2009/XPDL2.2">
  <PackageHeader>
    <XPDLVersion>2.2</XPDLVersion>
    <Vendor>Bizagi Process Modeler</Vendor>
    <Created>{self.timestamp}</Created>
    <ModificationDate>{self.timestamp}</ModificationDate>
    <Description>{self.process_name}</Description>
    <Documentation>&lt;p style="text-align:left;"&gt;{self.process_name}&lt;/p&gt;</Documentation>
  </PackageHeader>
  <RedefinableHeader>
    <Author>Made - S2 Grupo</Author>
    <Version>1.0</Version>
    <Countrykey>{self.country_code}</Countrykey>
  </RedefinableHeader>
  <ExternalPackages />
  <Participants>
{participants}
  </Participants>
  <Pools>
    <Pool Id="{self.pool_id}" Name="{self.process_name}" Process="{self.process_uuid}" BoundaryVisible="true">
      <Lanes>
{lanes}
      </Lanes>
      <NodeGraphicsInfos>
        <NodeGraphicsInfo ToolId="BizAgi_Process_Modeler" Height="{len(self.roles) * 100 + 100}" Width="1600" BorderColor="-16777216" FillColor="-1">
          <Coordinates XCoordinate="30" YCoordinate="30" />
          <TextDirection xsi:nil="true" />
        </NodeGraphicsInfo>
      </NodeGraphicsInfos>
    </Pool>
  </Pools>
  <WorkflowProcesses>
    <WorkflowProcess Id="{self.process_uuid}" Name="{self.process_name}">
      <ProcessHeader />
      <Activities>
{activities_xml}
      </Activities>
      <Transitions>
{transitions}
      </Transitions>
    </WorkflowProcess>
  </WorkflowProcesses>
  <ExtendedAttributes>
    <ExtendedAttribute Name="TIPO_x0020_DE_x0020_DOCUMENTO" Value="Proceso" />
    <ExtendedAttribute Name="CLASIFICACIÓN_x0020_DE_x0020_LA_x0020_INFORMACIÓN" Value="Sensible" />
    <ExtendedAttribute Name="Responsable_x0020_del_x0020_Proceso" Value="Dirección" />
  </ExtendedAttributes>
</Package>'''
        
        return xpdl
    
    def _generate_participants(self) -> str:
        """Genera Participants XML"""
        parts = []
        for role in self.roles:
            role_id = str(uuid.uuid4())
            parts.append(f'''    <Participant Id="{role_id}" Name="{role}">
      <ParticipantType Type="ROLE" />
      <Description>{role}</Description>
      <ExtendedAttributes>
        <ExtendedAttribute Name="{role.replace(' ', '')}" />
      </ExtendedAttributes>
    </Participant>''')
        return '\n'.join(parts)
    
    def _generate_lanes(self) -> Tuple[str, Dict]:
        """Genera Lanes XML y mapa de lanes por rol"""
        lanes_xml = []
        lane_map = {}
        y_coord = 0
        lane_height = 100
        
        for role in self.roles:
            lane_id = str(uuid.uuid4())
            lane_map[role] = {"id": lane_id, "y": y_coord}
            
            lanes_xml.append(f'''        <Lane Id="{lane_id}" Name="{role}" ParentPool="{self.pool_id}">
          <NodeGraphicsInfos>
            <NodeGraphicsInfo ToolId="BizAgi_Process_Modeler" Height="{lane_height}" Width="1500" BorderColor="-11513776" FillColor="-1">
              <Coordinates XCoordinate="50" YCoordinate="{y_coord}" />
              <TextDirection xsi:nil="true" />
            </NodeGraphicsInfo>
          </NodeGraphicsInfos>
          <ExtendedAttributes />
        </Lane>''')
            
            y_coord += lane_height
        
        return '\n'.join(lanes_xml), lane_map
    
    def _generate_activities(self, lane_map: Dict) -> Tuple[str, Dict]:
        """Genera Activities XML con gráficos"""
        activities_xml = []
        activity_map = {}
        x_coord = 150
        task_width = 90
        
        for i, act in enumerate(self.activities):
            act_id = str(uuid.uuid4())
            role = act['responsables'][0] if act['responsables'] else self.roles[0]
            lane_info = lane_map.get(role, lane_map[self.roles[0]])
            y_coord = lane_info['y'] + 20
            
            activity_map[i] = {
                "id": act_id,
                "name": act['name'],
                "x": x_coord,
                "y": y_coord
            }
            
            # Activity XML structure con Implementation, Performers, etc.
            activities_xml.append(f'''        <Activity Id="{act_id}" Name="{act['name']}">
          <Description>&lt;p&gt;{act.get('action', '')}&lt;/p&gt;</Description>
          <Implementation>
            <Task />
          </Implementation>
          <Performers>
            <Performer>{uuid.uuid4()}</Performer>
          </Performers>
          <Documentation>&lt;p&gt;{act.get('action', '')}&lt;/p&gt;</Documentation>
          <Loop LoopType="None" />
          <NodeGraphicsInfos>
            <NodeGraphicsInfo ToolId="BizAgi_Process_Modeler" Height="60" Width="{task_width}" BorderColor="{self.border_task}" FillColor="{self.task_color}">
              <Coordinates XCoordinate="{x_coord}" YCoordinate="{y_coord}" />
              <TextDirection xsi:nil="true" />
            </NodeGraphicsInfo>
          </NodeGraphicsInfos>
          <ExtendedAttributes>
            <ExtendedAttribute Name="BizagiAccountables" Value="{act['responsables'][0] if act['responsables'] else 'Sin asignar'}" />
          </ExtendedAttributes>
        </Activity>''')
            
            x_coord += 200
        
        return '\n'.join(activities_xml), activity_map
    
    def _generate_transitions(self, activity_map: Dict) -> str:
        """Genera Transitions XML"""
        transitions = []
        
        for i in range(len(self.activities) - 1):
            from_act = activity_map[i]
            to_act = activity_map[i + 1]
            
            # Calcular puntos de conexión
            from_x = from_act['x'] + 90
            from_y = from_act['y'] + 30
            to_x = to_act['x']
            to_y = to_act['y'] + 30
            
            trans_id = str(uuid.uuid4())
            
            transitions.append(f'''        <Transition Id="{trans_id}" From="{from_act['id']}" To="{to_act['id']}">
          <Condition />
          <Description />
          <ConnectorGraphicsInfos>
            <ConnectorGraphicsInfo ToolId="BizAgi_Process_Modeler" BorderColor="-16777216">
              <TextDirection xsi:nil="true" />
              <Coordinates XCoordinate="{from_x}" YCoordinate="{from_y}" />
              <Coordinates XCoordinate="{to_x}" YCoordinate="{to_y}" />
            </ConnectorGraphicsInfo>
          </ConnectorGraphicsInfos>
          <ExtendedAttributes />
        </Transition>''')
        
        return '\n'.join(transitions)


class BizagiBPMNGenerator:
    """Genera BPMN 2.0 con estructura Bizagi"""
    
    def __init__(self, process_id: str, process_name: str,
                 activities: List[Dict], roles: List[str]):
        self.process_id = process_id
        self.process_name = process_name
        self.activities = activities
        self.roles = roles
        self.process_uuid = str(uuid.uuid4())
    
    def generate(self) -> str:
        """Genera el BPMN completo"""
        
        # Start event
        start_id = str(uuid.uuid4())
        
        # Activities
        activities_xml = f'''    <startEvent id="{start_id}" name="Inicio" />
'''
        activity_ids = []
        
        for i, act in enumerate(self.activities):
            act_id = str(uuid.uuid4())
            activity_ids.append(act_id)
            
            activities_xml += f'''    <task id="{act_id}" name="{act['name']}">
      <documentation>{act.get('action', '')}</documentation>
      <extensionElements>
        <bizagi:BizagiExtensions xmlns:bizagi="http://www.bizagi.com/bpmn20">
          <bizagi:BizagiProperties>
            <bizagi:BizagiProperty name="performer" value="{act['responsables'][0] if act['responsables'] else 'Sin asignar'}" />
          </bizagi:BizagiProperties>
        </bizagi:BizagiExtensions>
      </extensionElements>
    </task>
'''
        
        # End event
        end_id = str(uuid.uuid4())
        activities_xml += f'''    <endEvent id="{end_id}" name="Fin" />
'''
        
        # Sequence flows
        flows_xml = f'''    <sequenceFlow id="Flow_Start" sourceRef="{start_id}" targetRef="{activity_ids[0]}" />
'''
        
        for i in range(len(activity_ids) - 1):
            flows_xml += f'''    <sequenceFlow id="Flow_{i+1}" sourceRef="{activity_ids[i]}" targetRef="{activity_ids[i+1]}" />
'''
        
        flows_xml += f'''    <sequenceFlow id="Flow_End" sourceRef="{activity_ids[-1]}" targetRef="{end_id}" />
'''
        
        # LaneSet
        lanes_xml = '    <laneSet id="LaneSet_1">\n'
        for i, role in enumerate(self.roles):
            lanes_xml += f'''      <lane id="Lane_{i+1}" name="{role}" />
'''
        lanes_xml += '    </laneSet>\n'
        
        bpmn = f'''<?xml version="1.0"?>
<definitions xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bizagi="http://www.bizagi.com/bpmn20" id="{self.process_uuid}" targetNamespace="http://www.bizagi.com/definitions/{self.process_uuid}" xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="{self.process_uuid}" name="{self.process_name}">
    <documentation>{self.process_name}</documentation>
{lanes_xml}{activities_xml}{flows_xml}
  </process>
</definitions>'''
        
        return bpmn


def process_text_to_xpdl_bpmn(process_id: str, process_name: str, country_code: str,
                              description: str) -> Tuple[str, str]:
    """Procesa texto y genera XPDL y BPMN"""
    
    # Parsear actividades y roles
    activities = []
    roles = set()
    
    lines = description.split('\n')
    current_activity = None
    
    for line in lines:
        # Detectar número de actividad
        num_match = re.match(r'^\s*(\d+)\.\s*(.+?)$', line)
        if num_match:
            if current_activity:
                activities.append(current_activity)
            current_activity = {
                'num': int(num_match.group(1)),
                'name': num_match.group(2).strip(),
                'responsables': [],
                'action': ''
            }
            continue
        
        # Detectar responsables
        resp_match = re.match(r'^Responsables?:\s*(.+?)$', line, re.IGNORECASE)
        if resp_match and current_activity:
            resp_text = resp_match.group(1)
            resp_list = re.split(r'\s+y\s+|\s*,\s*', resp_text)
            for resp in resp_list:
                resp = resp.strip()
                if resp:
                    current_activity['responsables'].append(resp)
                    roles.add(resp)
            continue
        
        # Detectar acción
        action_match = re.match(r'^Acción:\s*(.+?)$', line, re.IGNORECASE)
        if action_match and current_activity:
            current_activity['action'] = action_match.group(1).strip()
    
    if current_activity:
        activities.append(current_activity)
    
    roles_list = sorted(list(roles))
    
    # Generar XPDL
    xpdl_gen = BizagiXPDLGenerator(process_id, process_name, country_code, activities, roles_list)
    xpdl = xpdl_gen.generate()
    
    # Generar BPMN
    bpmn_gen = BizagiBPMNGenerator(process_id, process_name, activities, roles_list)
    bpmn = bpmn_gen.generate()
    
    return xpdl, bpmn


if __name__ == '__main__':
    # Prueba
    desc = """1. Identificación de necesidades
Responsable: Encargado de compras
Acción: Evaluar el inventario.

2. Investigación de proveedores
Responsable: Encargado de compras
Acción: Identificar proveedores."""
    
    xpdl, bpmn = process_text_to_xpdl_bpmn('SGP_TEST_P01', 'Test Proceso', 'ES', desc)
    
    print("=== XPDL (primeras 500 chars) ===")
    print(xpdl[:500])
    print("\n=== BPMN (primeras 500 chars) ===")
    print(bpmn[:500])
