# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

########################################################################################################################
## FET Pcells Generators for Klayout of GF180MCU
########################################################################################################################

from math import ceil, floor
import numpy as np

import gdsfactory as gf
from gdsfactory.types import Float2, LayerSpec
# from .via_generator import * 
from .layers_def import *

# @gf.cell
def draw_nfet(
    layout ,
    l : float = 0.28,
    w : float = 0.22,
    sd_con_col : int = 1,
    inter_sd_l : float = 0.24 ,
    nf : int = 1, 
    grw : float = 0.22 ,
    volt : str = "3.3V",
    bulk = "None",
    con_bet_fin : int = 1,
    gate_con_pos = "alternating",
    interdig : int = 0,
    patt = "",
    deepnwell: int = 0,
    pcmpgr : int = 0

)  -> gf.Component:

    '''
    Retern nfet

    Args: 
        layout : layout object 
        l : Float of gate length 
        w : Float of gate width
        sd_l : Float of source and drain diffusion length
        inter_sd_l : Float of source and drain diffusion length between fingers 
        nf : integer of number of fingers 
        M : integer of number of multipliers 
        grw : gaurd ring width when enabled 
        type : string of the device type 
        bulk : String of bulk connection type (None, Bulk Tie, Guard Ring)
        con_bet_fin : boolean of having contacts for diffusion between fingers
        gate_con_pos : string of choosing the gate contact position (bottom, top, alternating )

    '''
    # used layers and dimensions 
    
    end_cap: float = 0.22
    if volt == "3.3V" :
        comp_spacing : float = 0.28
        poly2_comp_spacing : float = 0.1
    else : 
        comp_spacing : float = 0.36
        poly2_comp_spacing : float = 0.3

    
    
    gate_np_enc : float = 0.23
    comp_np_enc : float = 0.16
    comp_pp_enc : float = 0.16
    
    
#     gate_npc_ext = 0.11
#     npc_spacing = 0.27 
   
    
#     gate_lvt_enc : float = 0.18
    
    
#     hv_enclosing : float = 0.185
    
    
#     areaid_lvn_enc : float = 0.1



    con_size = 0.22
    con_sp = 0.28
    con_comp_enc = 0.07
    con_pl_enc = 0.07


    sd_l_con = ((sd_con_col)*con_size) + ((sd_con_col-1)*con_sp) + 2*con_comp_enc
    sd_l = sd_l_con
    
    # gds components to store a single instance and the generated device 
    c = gf.Component("sky_nfet_dev")

    c_inst = gf.Component("dev_temp")

    # generating sd diffusion 
   
    
#     if interdig == 1 and nf >1 and nf != len(patt) and patt !="":
#         nf = len(patt)

    l_d = nf*l + (nf-1)*inter_sd_l + 2*(con_comp_enc) #  diffution total length 
    rect_d_intr = gf.components.rectangle(size = (l_d,w), layer= comp_layer)  
    sd_diff_intr = c_inst.add_ref(rect_d_intr)

#     # generatin sd contacts 

    if (w <= con_size+ 2*con_comp_enc) :
        cmpc_y = con_comp_enc + con_size + con_comp_enc
        
    else :
        cmpc_y = w 
    
    cmpc_size = (sd_l_con, cmpc_y)

    sd_diff = c_inst.add_array(
        component= gf.components.rectangle(size=cmpc_size,layer=comp_layer),
        rows=1,
        columns=2,
        spacing=(cmpc_size[0]+sd_diff_intr.size[0],0),
        )
    
    sd_diff.xmin = sd_diff_intr.xmin - cmpc_size[0]
    sd_diff.ymin = sd_diff_intr.ymin - (sd_diff.size[1]-sd_diff_intr.size[1])/2 

#     sd_con = via_stack(x_range = (0,sd_l),y_range=(0,w),base_layer=diff_layer,metal_level=1)
#     c_inst.add_array(component=sd_con,columns=2,rows=1,spacing=(sd_l+ nf*l + (nf-1)*inter_sd_l,0))



#     if con_bet_fin == 1 and nf>1: 
#         inter_sd_con = via_stack(x_range = (sd_l + l,sd_l + l+ inter_sd_l),y_range=(0,w),base_layer=diff_layer,metal_level=1)
#         c_inst.add_array(component=inter_sd_con,columns=nf-1,rows=1,spacing=(l+inter_sd_l,0))
   


#     # generating poly 

#     if (l <= licon_size[0]+ 2*licon_p_enc[0]) :
#         pc_x = licon_p_enc[0] +licon_size[0] + licon_p_enc[0]
        
#     else :
#         pc_x = l 
    
#     pc_size = (pc_x, licon_p_enc[1] +licon_size[1] + licon_p_enc[1])

#     c_pc  = gf.Component("poly con")

#     rect_pc = c_pc.add_ref(gf.components.rectangle(size=pc_size,layer=poly_layer))


#     poly_con = via_stack(x_range=(rect_pc.xmin, rect_pc.xmax),y_range=(rect_pc.ymin, rect_pc.ymax),base_layer=poly_layer,metal_level=1,li_enc_dir="H")
#     c_pc.add_ref(poly_con)

    if nf == 1 :
        poly = c_inst.add_ref(gf.components.rectangle(size=(l,w+2*end_cap),layer=poly2_layer))
        poly.xmin = sd_diff_intr.xmin + con_comp_enc
        poly.ymin = sd_diff_intr.ymin - end_cap

        # if gate_con_pos == "bottom":
        #     mv = 0
        #     nr = 1
        # elif gate_con_pos == "top" :
        #     mv = pc_size[1]+ w + 2*end_cap
        #     nr = 1
        # else :
        #     mv = 0 
        #     nr = 2
        
        # pc = c_inst.add_array(component=c_pc,rows=nr,columns=1, spacing=(0,pc_size[1]+w+2*end_cap))
        # pc.move((sd_l- ((pc_x - l)/2), -pc_size[1] - end_cap + mv))

        


    else :

        w_p1 = end_cap + w + end_cap  # poly total width

        # if inter_sd_l < (npc_spacing + 2*gate_npc_ext) :

        #     if gate_con_pos == "alternating":
        #         w_p1 += 0.2
        #         w_p2 = w_p1
        #         e_c = 0.2
        #     else : 
        #         w_p2 = w_p1 + licon_p_enc[1] +licon_size[1] + licon_p_enc[1] + npc_spacing + 0.1 
        #         e_c = 0

        #     if gate_con_pos == "bottom" :
        #         p_mv = -end_cap - (w_p2-w_p1)
        #     else : 
        #         p_mv = -end_cap

        # else : 

        w_p2 = w_p1
        p_mv = -end_cap
        e_c = 0
    
        rect_p1 = gf.components.rectangle(size = (l,w_p1), layer= poly2_layer)
        rect_p2 = gf.components.rectangle(size = (l,w_p2), layer= poly2_layer)
        poly1 = c_inst.add_array(rect_p1, rows= 1 , columns= ceil(nf/2) , spacing= [2*(inter_sd_l+l), 0 ])
        poly1.move((sd_l,-end_cap - e_c))


        poly2 = c_inst.add_array(rect_p2, rows= 1 , columns= floor(nf/2) , spacing= [2*(inter_sd_l+l), 0 ])
        poly2.move((sd_l+l+inter_sd_l,p_mv))


#         #generating poly contacts setups

#         if gate_con_pos == "bottom":
#             mv_1 = 0
#             mv_2 = - (w_p2-w_p1)
#         elif gate_con_pos == "top" :
#             mv_1 = pc_size[1]+ w_p1
#             mv_2 = pc_size[1]+ w_p2
#         else :
#             mv_1 = -e_c
#             mv_2 = pc_size[1]+ w_p2
    
        
#         nc1 = ceil(nf/2)
#         nc2 = floor(nf/2)
    
#         pc_spacing = 2*(inter_sd_l + l)

#         # generating poly contacts 
    
#         pc1 = c_inst.add_array(component=c_pc,rows=1,columns=nc1,spacing=(pc_spacing,0))
#         pc1.move((sd_l- ((pc_x - l)/2), -pc_size[1] - end_cap + mv_1))
        
#         pc2 = c_inst.add_array(component=c_pc,rows=1,columns=nc2,spacing=(pc_spacing,0))
#         pc2.move((sd_l- ((pc_x - l)/2) + (inter_sd_l + l), -pc_size[1] - end_cap + mv_2))

        

#         if interdig == 1 : 
#             if nf == len(patt): 
#                 pat = list(patt)
#                 nt = [] # list to store the symbols of transistors and thier number nt(number of transistors)
#                 [nt.append(x) for x in pat if x not in nt]
#                 nl = int(len(nt))

#                 m2_spacing = 0.14
#                 via1_size = (0.15,0.15)
#                 via1_enc = (0.085,0.055)
#                 via1_spacing = (0.17,0.17)
#                 via2_size = (0.2,0.2)
#                 via2_enc = (0.085,0.065)
#                 via2_spacing = (0.2,0.2)

#                 m2_y = via1_size[1]+2*via1_enc[1]
#                 m2 = gf.components.rectangle(size=(sd_diff.xmax - sd_diff.xmin, m2_y),layer=m2_layer)

#                 if gate_con_pos == "alternating":
#                     pat_o = []
#                     pat_e = []

#                     for i in range(int(nf)):
#                         if i%2 == 0 :
#                             pat_e.append(pat[i])
#                         else :
#                             pat_o.append(pat[i])
                    
#                     nt_o = []
#                     [nt_o.append(x) for x in pat_o if x not in nt_o]

#                     nt_e = []
#                     [nt_e.append(x) for x in pat_e if x not in nt_e]

#                     nl_b = len(nt_e)
#                     nl_u = len(nt_o)
                    
#                     m2_y = via2_size[1]+2*via2_enc[1]
#                     m2 = gf.components.rectangle(size=(sd_diff.xmax - sd_diff.xmin, m2_y),layer=m2_layer)

#                     m2_arrb = c_inst.add_array(component=m2, columns=1, rows=nl_b,spacing= (0, -m2_y - m2_spacing))
#                     m2_arrb.movey(pc1.ymin - m2_spacing - m2_y)

#                     m2_arru =  c_inst.add_array(component=m2, columns=1, rows=nl_u,spacing= (0, m2_y + m2_spacing))
#                     m2_arru.movey(pc2.ymax + m2_spacing)


#                     for i in range(nl_u):
#                         for j in range(floor(nf/2)):
#                             if pat_o[j] == nt_o[i]:
#                                 m1 = c_inst.add_ref(gf.components.rectangle(
#                                     size=(poly_con.xmax - poly_con.xmin , ((pc2.ymax + (i+1)*(m2_spacing+ m2_y)) - pc2.ymin )),layer=m1_layer))
#                                 m1.move(((sd_l- ((poly_con.xmax - poly_con.xmin - l)/2) + (2*j +1)*(l+inter_sd_l))
#                                 , (pc2.ymin+0.06)))
#                                 via1_dr = via_generator(x_range=(m1.xmin,m1.xmax),y_range=(m2_arru.ymin + i*(m2_y+m2_spacing),m2_arru.ymin + i*(m2_y+m2_spacing)+m2_y)
#                                 , via_enclosure=via1_enc,via_layer=via1_layer,via_size=via1_size,via_spacing=via1_spacing)
#                                 via1 = c_inst.add_ref(via1_dr)
#                                 c_inst.add_label(f"{pat_o[j]}",position=((via1.xmax+via1.xmin)/2, (via1.ymax+via1.ymin)/2),layer=m1_lbl)
                                
                                
                    
#                     for i in range(nl_b):
#                         for j in range(ceil(nf/2)):
#                             if pat_e[j] == nt_e[i]:
                                
#                                 m1 = c_inst.add_ref(gf.components.rectangle(
#                                     size=(poly_con.xmax - poly_con.xmin , ((pc1.ymax + (i+1)*(m2_spacing+ m2_y)) -pc1.ymin )),layer=m1_layer))
#                                 m1.move(((sd_l- ((poly_con.xmax - poly_con.xmin - l)/2) + (2*j)*(l+inter_sd_l)), -(m1.ymax - m1.ymin) + (pc1.ymax-0.06)))
#                                 via1_dr = via_generator(x_range=(m1.xmin,m1.xmax),y_range=(m2_arrb.ymax - i*(m2_spacing+m2_y) - m2_y,m2_arrb.ymax - i*(m2_spacing+m2_y))
#                                 , via_enclosure=via1_enc,via_layer=via1_layer,via_size=via1_size,via_spacing=via1_spacing)
#                                 via1 = c_inst.add_ref(via1_dr)
#                                 c_inst.add_label(f"{pat_e[j]}",position=((via1.xmax+via1.xmin)/2, (via1.ymax+via1.ymin)/2),layer=m1_lbl)
                                
                                
                    
#                     m3_x = via2_size[0] + 2*via2_enc[0]
#                     m3_spacing = 0.3
                    
#                     for i in range(nl_b):
#                         for j in range(nl_u):
#                             if nt_e[i] == nt_o[j]:
                                
#                                 m2_join_b = c_inst.add_ref(gf.components.rectangle(size=(m2_y+ (i+1)*(m3_spacing+m3_x),m2_y),layer=m2_layer)
#                                 .move((m2_arrb.xmin -(m2_y + (i+1)*(m3_spacing+m3_x)),m2_arrb.ymax - i*(m2_spacing+m2_y) - m2_y)))
#                                 m2_join_u = c_inst.add_ref(gf.components.rectangle(size=(m2_y+ (i+1)*(m3_spacing+m3_x),m2_y),layer=m2_layer)
#                                 .move((m2_arru.xmin -( m2_y + (i+1)*(m3_spacing+m3_x) ),m2_arru.ymin + j*(m2_spacing+m2_y))))
#                                 m3 = c_inst.add_ref(gf.components.rectangle(size=(m3_x, m2_join_u.ymax - m2_join_b.ymin),layer=m1_layer))
#                                 m3.move((m2_join_b.xmin,m2_join_b.ymin))
#                                 via2_dr = via_generator(x_range=(m3.xmin,m3.xmax),y_range=(m2_join_b.ymin,m2_join_b.ymax),via_enclosure=via1_enc,via_size=via1_size
#                                 ,via_layer=via1_layer,via_spacing=via1_spacing)
#                                 via2 = c_inst.add_array(component=via2_dr,columns=1,rows=2,spacing=(0,m2_join_u.ymin-m2_join_b.ymin))
                                

                
#                 elif gate_con_pos == "top" :
                    
#                     m2_arr = c_inst.add_array(component=m2, columns=1, rows=nl , spacing=(0,m2.ymax-m2.ymin + m2_spacing))
#                     m2_arr.movey(pc2.ymax + m2_spacing)
                    
#                     for i in range(nl):
#                         for j in range(int(nf)):
#                             if pat[j] == nt[i]:
#                                 m1 = c_inst.add_ref(gf.components.rectangle(
#                                     size=(poly_con.xmax - poly_con.xmin , ((pc2.ymax + (i+1)*(m2_spacing+ m2_y)) - ((1-j%2)*pc1.ymin) - (j%2)*pc2.ymin )),layer=m1_layer))
#                                 m1.move(((sd_l- ((poly_con.xmax - poly_con.xmin - l)/2) + j*(l+inter_sd_l))
#                                 , (1-j%2)*(pc1.ymin+0.06) + (j%2)*(pc2.ymin+0.06)))
#                                 via1_dr = via_generator(x_range=(m1.xmin,m1.xmax),y_range=(m2_arr.ymin + i*(m2_spacing+m2_y),m2_arr.ymin + i*(m2_spacing+m2_y)+m2_y)
#                                 , via_enclosure=via1_enc,via_layer=via1_layer,via_size=via1_size,via_spacing=via1_spacing)
#                                 via1 = c_inst.add_ref(via1_dr)
#                                 c_inst.add_label(f"{pat[j]}",position=((via1.xmax+via1.xmin)/2, (via1.ymax+via1.ymin)/2),layer=m1_lbl)
                                


#                 elif gate_con_pos == "bottom" :
                    
#                     m2_arr = c_inst.add_array(component=m2, columns=1, rows=nl , spacing=(0,-m2_y - m2_spacing))
#                     m2_arr.movey(pc2.ymin - m2_spacing - m2_y)
                    
#                     for i in range(nl):
#                         for j in range(int(nf)):
#                             if pat[j] == nt[i]:
                                
#                                 m1 = c_inst.add_ref(gf.components.rectangle(
#                                     size=(poly_con.xmax - poly_con.xmin , ((pc1.ymax + (i+1)*(m2_spacing+ m2_y)) - (j%2)*pc1.ymin  - (1-j%2)*pc2.ymin)),layer=m1_layer))
#                                 m1.move(((sd_l- ((poly_con.xmax - poly_con.xmin - l)/2) + j*(l+inter_sd_l)), -(m1.ymax - m1.ymin) + (1-j%2)*(pc1.ymax-0.06)+ (j%2)*(pc2.ymax-0.06)))
#                                 via1_dr = via_generator(x_range=(m1.xmin,m1.xmax),y_range=(m2_arr.ymax - i*(m2_spacing+m2_y) -m2_y,m2_arr.ymax - i*(m2_spacing+m2_y) )
#                                 , via_enclosure=via1_enc,via_layer=via1_layer,via_size=via1_size,via_spacing=via1_spacing)
#                                 via1 = c_inst.add_ref(via1_dr)
#                                 c_inst.add_label(f"{pat[j]}",position=((via1.xmax+via1.xmin)/2, (via1.ymax+via1.ymin)/2),layer=m1_lbl)
                                
                    
   

    
    
    # generating bulk 
    if bulk == "None":
        nplus = c_inst.add_ref(gf.components.rectangle(size=(sd_diff.size[0]+ 2*comp_np_enc, w+ 2*gate_np_enc),layer= nplus_layer))
        nplus.xmin = sd_diff.xmin - comp_np_enc
        nplus.ymin = sd_diff_intr.ymin - gate_np_enc

        # if type=="sky130_fd_pr__nfet_g5v0d10v5" or type== "sky130_fd_pr__nfet_05v0_nvt" or type == "sky130_fd_pr__nfet_03v3_nvt":
        #     hvntm = c_inst.add_ref(gf.components.rectangle(size=(l_d+2*hv_enclosing,w+2*hv_enclosing),layer=hvntm_layer))
        #     hvntm.move((sd_diff.xmin - hv_enclosing, sd_diff.ymin- hv_enclosing))

    
#     elif bulk == "bulk tie":
#         rect_bulk = c_inst.add_ref(gf.components.rectangle(size=(sd_l*1.5,w),layer=tap_layer))
#         rect_bulk.connect("e1",destination=sd_diff.ports["e3"])
#         nsdm = c_inst.add_ref(gf.components.rectangle(size=(sd_diff.xmax - sd_diff.xmin +diff_nsdm_enc,w + 2*diff_nsdm_enc),layer=nsdm_layer))
#         nsdm.move((-diff_nsdm_enc,-diff_nsdm_enc))
#         psdm = c_inst.add_ref(gf.components.rectangle(size=(rect_bulk.xmax - rect_bulk.xmin +tap_psdm_enc, w+ 2*tap_psdm_enc), layer= psdm_layer))
#         psdm.connect("e1",destination = nsdm.ports["e3"])

#         bulk_con = via_stack(x_range= (rect_bulk.xmin+0.1,rect_bulk.xmax-0.1),y_range=(rect_bulk.ymin,rect_bulk.ymax),base_layer=tap_layer,metal_level=0)
#         c_inst.add_ref(bulk_con)
        

#         if type=="sky130_fd_pr__nfet_g5v0d10v5" or type== "sky130_fd_pr__nfet_05v0_nvt" or type == "sky130_fd_pr__nfet_03v3_nvt":
#             hvntm = c_inst.add_ref(gf.components.rectangle(size=(l_d+hv_enclosing,w+2*hv_enclosing),layer=hvntm_layer))
#             hvntm.move((sd_diff.xmin - hv_enclosing, sd_diff.ymin- hv_enclosing))
        
        



#     elif bulk == "Gaurd Ring":
        
#         nsdm = c_inst.add_ref(gf.components.rectangle(size=(l_d+ 2*diff_nsdm_enc, w+ 2*diff_nsdm_enc),layer= nsdm_layer))
#         nsdm.move((-diff_nsdm_enc,-diff_nsdm_enc))
#         c.add_ref(c_inst)

#         c_temp = gf.Component("temp_store")
#         rect_bulk_in = c_temp.add_ref(gf.components.rectangle(size=((c_inst.xmax - c_inst.xmin) + 2*diff_tap_spacing,
#         (c_inst.ymax - c_inst.ymin)  +  2*poly_tap_spacing )
#         , layer= tap_layer))
#         rect_bulk_in.move((c_inst.xmin -diff_tap_spacing,c_inst.ymin - poly_tap_spacing))
#         rect_bulk_out = c_temp.add_ref(gf.components.rectangle(size=((rect_bulk_in.xmax - rect_bulk_in.xmin) + 2*grw,(rect_bulk_in.ymax - rect_bulk_in.ymin) + 2*grw )
#         , layer= tap_layer))
#         rect_bulk_out.move((rect_bulk_in.xmin - grw , rect_bulk_in.ymin -grw ))
#         B = c.add_ref(gf.geometry.boolean(A= rect_bulk_out , B = rect_bulk_in , operation= "A-B", layer= tap_layer) )
        
#         psdm_in = c_temp.add_ref(gf.components.rectangle(size=((rect_bulk_in.xmax - rect_bulk_in.xmin) - 2*tap_psdm_enc, (rect_bulk_in.ymax - rect_bulk_in.ymin) - 2*tap_psdm_enc )
#         , layer= psdm_layer))
#         psdm_in.move((rect_bulk_in.xmin + tap_psdm_enc, rect_bulk_in.ymin + tap_psdm_enc))
#         psdm_out = c_temp.add_ref(gf.components.rectangle(size=((rect_bulk_out.xmax - rect_bulk_out.xmin) + 2*tap_psdm_enc, (rect_bulk_out.ymax - rect_bulk_out.ymin) + 2*tap_psdm_enc )
#         , layer= nsdm_layer))
#         psdm_out.move((rect_bulk_out.xmin - tap_psdm_enc, rect_bulk_out.ymin - tap_psdm_enc))
#         psdm = c.add_ref(gf.geometry.boolean(A= psdm_out , B = psdm_in , operation= "A-B", layer= psdm_layer) )



#         # generating contacts


#         ring_con_bot = c.add_ref(via_generator(x_range=(rect_bulk_in.xmin + 0.17,rect_bulk_in.xmax-0.17),y_range=(rect_bulk_out.ymin,rect_bulk_in.ymin)
#             , via_enclosure=licon_dt_enc, via_layer=licon_layer,via_size=licon_size,via_spacing=licon_spacing))

#         ring_con_up = c.add_ref(via_generator(x_range=(rect_bulk_in.xmin+0.17,rect_bulk_in.xmax-0.17),y_range=(rect_bulk_in.ymax,rect_bulk_out.ymax)
#             , via_enclosure=licon_dt_enc, via_layer=licon_layer,via_size=licon_size,via_spacing=licon_spacing))

#         ring_con_r = c.add_ref(via_generator(x_range=(rect_bulk_out.xmin,rect_bulk_in.xmin),y_range=(rect_bulk_in.ymin+0.17,rect_bulk_in.ymax-0.17)
#             , via_enclosure=licon_dt_enc, via_layer=licon_layer,via_size=licon_size,via_spacing=licon_spacing))

#         ring_con_l = c.add_ref(via_generator(x_range=(rect_bulk_in.xmax,rect_bulk_out.xmax),y_range=(rect_bulk_in.ymin+0.17,rect_bulk_in.ymax-0.17)
#             , via_enclosure=licon_dt_enc, via_layer=licon_layer,via_size=licon_size,via_spacing=licon_spacing))

#         tap_li_in = c_temp.add_ref(gf.components.rectangle(size=((l_d ) + 2*diff_tap_spacing,
#        (c_inst.ymax - c_inst.ymin) +  2*poly_tap_spacing )
#         , layer= li_layer))
#         tap_li_in.move((-diff_tap_spacing,c_inst.ymin - poly_tap_spacing))
#         tap_li_out = c_temp.add_ref(gf.components.rectangle(size=((rect_bulk_in.xmax - rect_bulk_in.xmin) + 2*grw,(rect_bulk_in.ymax - rect_bulk_in.ymin) + 2*grw )
#         , layer= li_layer))
#         tap_li_out.move((rect_bulk_in.xmin - grw , rect_bulk_in.ymin -grw ))
#         li = c.add_ref(gf.geometry.boolean(A= rect_bulk_out , B = rect_bulk_in , operation= "A-B", layer= li_layer) )

        

#         # generating hvi for high voltage 
#         if type=="sky130_fd_pr__nfet_g5v0d10v5" or type== "sky130_fd_pr__nfet_05v0_nvt" or type == "sky130_fd_pr__nfet_03v3_nvt":
#             hvi = c.add_ref(gf.components.rectangle(size=(rect_bulk_out.xmax-rect_bulk_out.xmin + 2*hv_enclosing
#             , rect_bulk_out.ymax - rect_bulk_out.ymin + 2*hv_enclosing),layer=hvi_layer))
#             hvi.move((rect_bulk_out.xmin-hv_enclosing, rect_bulk_out.ymin-hv_enclosing))

            
#             hvntm = c_inst.add_ref(gf.components.rectangle(size=(l_d+2*hv_enclosing,w+2*hv_enclosing),layer=hvntm_layer))
#             hvntm.move((sd_diff.xmin - hv_enclosing, sd_diff.ymin- hv_enclosing))



#     if bulk != "Gaurd Ring":
#         c.add_ref(c_inst)


#         # generating hvi and hvntm for high voltage 
#         if type=="sky130_fd_pr__nfet_g5v0d10v5" or type== "sky130_fd_pr__nfet_05v0_nvt" or type == "sky130_fd_pr__nfet_03v3_nvt" :
#             hvi = c.add_ref(gf.components.rectangle(size=(c_inst.xmax-c_inst.xmin + 2*hv_enclosing
#             , (c_inst.ymax - c_inst.ymin )+ 2*hv_enclosing),layer=hvi_layer))
#             hvi.move((c_inst.xmin-hv_enclosing, c_inst.ymin-hv_enclosing))



    
#     if type == "sky130_fd_pr__nfet_01v8_lvt":
#         lvt = c_inst.add_ref(gf.components.rectangle(size= (nf*l + (nf-1)*inter_sd_l + 2*gate_lvt_enc, w + 2*gate_lvt_enc)
#         , layer= lvtn_layer))
#         lvt.move((sd_l - gate_lvt_enc,-gate_lvt_enc))
    
#     if type ==  "sky130_fd_pr__nfet_03v3_nvt" or type == "sky130_fd_pr__nfet_05v0_nvt":

#         nvt = c_inst.add_ref(gf.components.rectangle(size= (nf*l + (nf-1)*inter_sd_l + 2*gate_lvt_enc, w + 2*gate_lvt_enc)
#         , layer= lvtn_layer))
#         nvt.move((sd_l - gate_lvt_enc,-gate_lvt_enc))

#         if type == "sky130_fd_pr__nfet_03v3_nvt" :
#             areaid_lvn = gf.components.rectangle(size=(l+2*areaid_lvn_enc,w+2*areaid_lvn_enc),layer=areaid_lvn_layer)
#             areaid_lvn_arr = c_inst.add_array(component=areaid_lvn,columns=nf,rows=1,spacing=[l+inter_sd_l,0])
#             areaid_lvn_arr.move((sd_l-areaid_lvn_enc , sd_diff.ymin - areaid_lvn_enc))

    c.add_ref(c_inst)
    # creating layout and cell in klayout 
    c.write_gds(f"nfet_temp.gds")
    layout.read(f"nfet_temp.gds")
    cell_name = "sky_nfet_dev"


    return layout.cell(cell_name)
    # return c

if __name__ == "__main__":
    c = draw_nfet()
    c.show()
    