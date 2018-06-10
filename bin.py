list=[8,9,10,11,12,13]

i=0
j=5

k=11


while i<=j:
	#print(str(i)+" "+str(j))
	m=(i+j)/2
	s=int(m)
	
	if(list[s]==k):
		print("Value found") 
		
	if(list[s]<k):
		i=s+1
	else:
		j=s-1
#print ("nOT FOUND")