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

#print("out data",out_data)
r_fp = open("enc_out.txt","r")
i=0
for i in range(len(out_data)):
    if(out_data[i] != int((str)(r_fp.readline()))):
        print("error",i)

#viterbi decode

def bmc(rx_pair,end_state):
    before_state0 = end_state[1:]
    before_state1 = end_state[1:]
    before_state0.append(0)
    before_state1.append(1)
    #print(before_state0)
    #print(before_state1)
    before_state0_out = []
    before_state0_out.append((end_state[0])^before_state0[1]^before_state0[2]^before_state0[4]^before_state0[5])
    before_state0_out.append((end_state[0])^before_state0[0]^before_state0[1]^before_state0[3]^before_state0[5])
    before_state0_out.append((end_state[0])^before_state0[0]^before_state0[1]^before_state0[2]^before_state0[5])

    before_state1_out = []
    before_state1_out.append((end_state[0])^before_state1[1]^before_state1[2]^before_state1[4]^before_state1[5])
    before_state1_out.append((end_state[0])^before_state1[0]^before_state1[1]^before_state1[3]^before_state1[5])
    before_state1_out.append((end_state[0])^before_state1[0]^before_state1[1]^before_state1[2]^before_state1[5])
    cost0 = (rx_pair[0]^before_state0_out[0]) + (rx_pair[1]^before_state0_out[1]) + (rx_pair[2]^before_state0_out[2]) 
    cost1 = (rx_pair[0]^before_state1_out[0]) + (rx_pair[1]^before_state1_out[1]) + (rx_pair[2]^before_state1_out[2]) 
    return [cost0,cost1]

def acs(cost,cost_pre,cost_valid):
    cost0_sum = cost[0] + cost_pre[0] 
    cost1_sum = cost[1] + cost_pre[1] 
    valid = 1 
    sel_cost = 0
    if(cost_valid[0] and cost_valid[1]):
        sel = 0 if (cost0_sum <= cost1_sum) else 1
        sel_cost = cost0_sum if (cost0_sum <= cost1_sum) else cost1_sum 
    elif(cost_valid[0]):
        sel = 0 
        sel_cost = cost0_sum 
    elif(cost_valid[1]):
        sel = 1 
        sel_cost = cost1_sum 
    else:
        valid = 0
        sel   = 0
    return [valid,sel,sel_cost]

def viterbi_decoder(init_valid_bit,rx_bitstream,DECODE_LEN):
    path_cost=[0]*64
    path_cost_next=[0]*64
    cost_valid=[0]*64
    cost_valid_next=[0]*64
    cost_valid[init_valid_bit] = 1 #first valid
    sel_ram=[[0 for t in range(64)] for x in range(DECODE_LEN)]
    i=0
    for i in range(0,DECODE_LEN):
        rxbits = [rx_bitstream[i*3+0], rx_bitstream[i*3+1], rx_bitstream[i*3+2]]
        bmc_cost=[[0 for y in range(2)] for z in range(64)]
        j=0
        for j in range(0,64):
            end_state = [j&1,(j>>1)&1,(j>>2)&1,(j>>3)&1,(j>>4)&1,(j>>5)&1]
            #end_state.reverse
            bmc_cost[j] = bmc(rxbits,end_state)

        j=0
        for j in range(0,64):
            idx_bits = [j&1,(j>>1)&1,(j>>2)&1,(j>>3)&1,(j>>4)&1,(j>>5)&1]
            idx0_bits = idx_bits.copy()
            idx0_bits=idx0_bits[1:]
            idx0_bits.append(0)
            idx0 = idx0_bits[0] + idx0_bits[1]*2 + idx0_bits[2]*4 + idx0_bits[3]*8 + idx0_bits[4]*16 + idx0_bits[5]*32

            idx1_bits = idx_bits.copy()
            idx1_bits=idx1_bits[1:]
            idx1_bits.append(1)
            idx1 = idx1_bits[0] + idx1_bits[1]*2 + idx1_bits[2]*4 + idx1_bits[3]*8 + idx1_bits[4]*16 + idx1_bits[5]*32

            acs_res=acs(bmc_cost[j],[path_cost[idx0],path_cost[idx1]],[cost_valid[idx0],cost_valid[idx1]])
            cost_valid_next[j] = acs_res[0]
            sel_ram[i][j] = acs_res[1] 
            path_cost_next[j]  = acs_res[2]

        j=0
        for j in range(0,64):
             cost_valid[j] = cost_valid_next[j]
             path_cost[j]  = path_cost_next[j]

    #print(path_cost)

    #trace back
    i=0
    min_path_id = path_cost.index(min(path_cost)) #DECODE_LEN>=64,else need to choose cost_valid
    decode_bits=[]
    sel_ram_idx = min_path_id
    for i in range(DECODE_LEN):
        sel_bits = [sel_ram_idx&1,(sel_ram_idx>>1)&1,(sel_ram_idx>>2)&1,(sel_ram_idx>>3)&1,(sel_ram_idx>>4)&1,(sel_ram_idx>>5)&1]
        decode_bits.insert(-(i+1),sel_bits[0])
        #update for before path
        new_sel_bits = sel_bits[1:]
        new_sel_bits.append(sel_ram[DECODE_LEN-i-1][sel_ram_idx])
        sel_ram_idx = new_sel_bits[0] + new_sel_bits[1]*2 + new_sel_bits[2]*4 + new_sel_bits[3]*8 + new_sel_bits[4]*16 + new_sel_bits[5]*32

    return [min_path_id,decode_bits]

i=0
decode_bits = []

#ERR
init_path = 0
dec_res=[]
for i in range(12): #decode 1200bits
    dec_res=(viterbi_decoder(init_path,out_data[i*300:i*300+300],100))
    init_path = dec_res[0]  
    decode_bits.extend(dec_res[1])

#decode_bits.extend(viterbi_decoder(out_data[300:600],100)) #ERR
#decode_bits.extend(viterbi_decoder(out_data,1200))
encin_fp = open("enc_in.txt","r")
i = 0
err_flag = 0
for x in encin_fp:
    if( (int)(x) != decode_bits[i]):
        err_flag = 1
        print("DECODE FAIL AT ",i)
    i=i+1

if(err_flag==0):
    print("DECODE ALL PASS")
