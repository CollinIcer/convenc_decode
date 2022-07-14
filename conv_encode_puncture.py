#conv_encode
state = [0,0,0,0,0,0] 
in_fp = open("enc_in.txt","r")
out_data = []
#ranbit=[]
i=0
#print("init state",state)
#once a bit
for x in in_fp: 
    #ranbit.append(state[0])
    out_data.append((int(x))^state[1]^state[2]^state[4]^state[5])
    out_data.append((int(x))^state[0]^state[1]^state[3]^state[5])
    out_data.append((int(x))^state[0]^state[1]^state[2]^state[5])
    state.insert(0,(int(x)))
    del state[-1]
    i=i+1

coding_rate = 2 

out_r1=[]
for i in range(3600):
    if(coding_rate==0):
        out_r1.append(out_data[i])
    elif(coding_rate==1):
        if((i%3)!=1): 
            out_r1.append(out_data[i])
    elif(coding_rate==2):
        id = i%15
        if( id==0 or id==1 or id==5 or id==6 or id==7 or id==11 or id==12 or id==13): 
            out_r1.append(out_data[i])
    elif(coding_rate==3):
        id = i%9
        if(id==0 or id==1 or id==5 or id==8): 
            out_r1.append(out_data[i])
    if(len(out_r1)==1200):
        break


r1_fp = open("renc_out.dat","w")
for i in range(len(out_r1)//15):
    for j in range(15):
        r1_fp.write(str(out_r1[i*15+j]))
        if(j==14):
            r1_fp.write("\n")

#module uwb_conv_encode(
#    input             init,         
#    input  [1:0]      coding_rate, //0:1/3 , 1: 1/2, 2: 5/8, 3: 3/4
#    input             datin_vld,
#    input  [4:0]      datin,       //hsb is first bit, info bits of 6 ofdm-frame is mutiples of 5
#    output            datout_vld,
#    output     [14:0] datout,     //{A,B,C} in spec, coding bits of 6 ofdm is always mutiples of 3
#
#    input             clk,
#    input resetn
#);
#
#reg [5:0] state;
#reg [1:0] enc_cnt;
#always @(posedge clk or negedge resetn)
#if(!resetn) begin
#    state <= 6'd0;
#    enc_cnt <= 'd0;
#end else if(init) begin
#    state <= 6'd0;
#    enc_cnt <= 'd0;
#end else if(datin_vld) begin
#    state <= {state[0],datin[4:0]};
#    enc_cnt <= enc_cnt=='d2 ? 'd0 : enc_cnt + 'd1;
#end
#
#function [2:0] enc_res(input f_din,input [5:0] f_state);
#begin
#    enc_res[2] = f_din^f_state[1]^f_state[2]^f_state[4]^f_state[5];
#    enc_res[1] = f_din^f_state[0]^f_state[1]^f_state[3]^f_state[5];
#    enc_res[0] = f_din^f_state[0]^f_state[1]^f_state[2]^f_state[5];
#end
#endfunction
#
#wire [2:0] enc_res0 = enc_res(datin[4],state);
#wire [2:0] enc_res1 = enc_res(datin[3],{state[4:0],datin[4]  });
#wire [2:0] enc_res2 = enc_res(datin[2],{state[3:0],datin[4:3]});
#wire [2:0] enc_res3 = enc_res(datin[1],{state[2:0],datin[4:2]});
#wire [2:0] enc_res4 = enc_res(datin[0],{state[1:0],datin[4:1]});
#
#// 1/3 coding rate
#wire rate0_datout_vld     = datin_vld;
#wire [14:0] rate0_datout  = {enc_res0,enc_res1,enc_res2,enc_res3,enc_res4}; 
#
#//1/2
#wire [9:0] rate1_enc_res =  {enc_res0[2],enc_res0[0] ,
#                             enc_res1[2],enc_res1[0] ,
#                             enc_res2[2],enc_res2[0] ,
#                             enc_res3[2],enc_res3[0] ,
#                             enc_res4[2],enc_res4[0]};
#//5/8
#wire [9:0] rate2_enc_res = {enc_res0[2:1],enc_res1[0],enc_res2[2:1],enc_res3[0],enc_res4[2:1],2'b0};
#
#// 3/4
#wire [9:0] rate3_enc_res = enc_cnt=='d0 ? {enc_res0[2:1],enc_res1[0]  ,enc_res2[0]  ,enc_res3[2:1],enc_res4[0]  ,3'd0} :
#                           enc_cnt=='d1 ? {enc_res0[0]  ,enc_res1[2:1],enc_res2[0]  ,enc_res3[0]  ,enc_res4[2:1],3'd0} : 
#                                          {enc_res0[0]  ,enc_res1[0]  ,enc_res2[2:1],enc_res3[0]  ,enc_res4[0]  ,4'd0} ;
#
#wire [3:0] rate3_enc_bits     = enc_cnt=='d2 ? 4'd6 : 4'd7;
#
#wire [9:0]  oth_rate_enc_res  = coding_rate=='d1 ? rate1_enc_res : 
#                                coding_rate=='d2 ? rate2_enc_res :  rate3_enc_res;
#wire [3:0]  oth_rate_enc_bits = coding_rate=='d1 ? 'd10 :  
#                                coding_rate=='d2 ? 'd8  : rate3_enc_bits;
#
#reg [13:0]  enc_buf;
#reg [3:0]   enc_buf_has_bits;
#wire [4:0]  enc_buf_has_bits_inc = datin_vld ? enc_buf_has_bits + oth_rate_enc_bits : enc_buf_has_bits;
#wire        rate_oth_dout_vld = enc_buf_has_bits_inc >= 'd15; 
#wire [3:0]  enc_buf_has_bits_in  = enc_buf_has_bits_inc - (rate_oth_dout_vld ? 4'd15 : 'd0); 
#
#wire [14:0] rate_oth_dout = datout_vld ? {enc_buf,1'd0} | (oth_rate_enc_res >> (enc_buf_has_bits-'d5)) : 'd0;
#
#wire [13:0] enc_buf_in = rate_oth_dout_vld ? {oth_rate_enc_res,4'd0} << (15-enc_buf_has_bits) : 
#                         datin_vld         ? enc_buf | ({oth_rate_enc_res,4'd0} >> enc_buf_has_bits) : 
#                         enc_buf; 
#
#always @(posedge clk or negedge resetn)
#if(!resetn) begin
#    enc_buf          <='d0; 
#    enc_buf_has_bits <='d0; 
#end else if(init) begin
#    enc_buf          <='d0; 
#    enc_buf_has_bits <='d0; 
#end else begin
#    enc_buf          <= enc_buf_in;
#    enc_buf_has_bits <=  enc_buf_has_bits_in;
#end
#
#assign    datout_vld = coding_rate=='d0 ? rate0_datout_vld : rate_oth_dout_vld;
#assign    datout     = coding_rate=='d0 ? rate0_datout     : rate_oth_dout;
#
#endmodule