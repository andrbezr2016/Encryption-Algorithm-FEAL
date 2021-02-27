import numpy as np
import time
start_time = time.time()

class FEAL():
	def __init__(self, round):
		self.round = round
		self.roundK = int((round/2)+4)
		self.block = 8 #байт

	def __leftRotate(self,n):
		return (n << 2)&0b11111111|(n >> 6)

	def S(self,a,b,n):
		if n=='0':
			return FEAL.__leftRotate(self,(a+b) % 256)
		elif n=='1':
			return FEAL.__leftRotate(self,(a+b+1) % 256)
		else:
			print('error S()')

	def F(self,a,b):
		F1=a[1]^b[0]^a[0]
		F2=a[2]^b[1]^a[3]
		F1=FEAL.S(self,F1,F2,'1')
		F2=FEAL.S(self,F2,F1,'0')
		F0=FEAL.S(self,a[0],F1,'0')
		F3=FEAL.S(self,a[3],F2,'1')
		return [F0,F1,F2,F3]

	def Fk(self,a,b):
		Fk1=a[1]^a[0]
		Fk2=a[2]^a[3]
		Fk1=FEAL.S(self,Fk1,Fk2^b[0],'1')
		Fk2=FEAL.S(self,Fk2,Fk1^b[1],'0')
		Fk0=FEAL.S(self,a[0],Fk1^b[2],'0')
		Fk3=FEAL.S(self,a[3],Fk2^b[3],'1')
		return [Fk0,Fk1,Fk2,Fk3]

	def roundKeyGen(self,K0):
		A=np.zeros((self.roundK+1,4), dtype=int)
		B=np.zeros((self.roundK+1,4), dtype=int)
		D=np.zeros((self.roundK+1,4), dtype=int)
		K=[]
		A[0]=[K0[0],K0[1],K0[2],K0[3]]
		B[0]=[K0[4],K0[5],K0[6],K0[7]]
		for k in range(1,self.roundK+1):
			FFk=FEAL.Fk(self,A[k-1],[B[k-1][0]^D[k-1][0],B[k-1][1]^D[k-1][1],B[k-1][2]^D[k-1][2],B[k-1][3]^D[k-1][3]])
			D[k]=A[k-1]
			A[k]=B[k-1]
			K.extend(FFk)
		return K

	def encryptBlock(self,P,K):
		L=np.zeros((self.round+1,4), dtype=int)
		R=np.zeros((self.round+1,4), dtype=int)
		C=[]
		L[0]=[P[0],P[1],P[2],P[3]]
		R[0]=[P[4],P[5],P[6],P[7]]
		for i in range(4):
			L[0][i]=L[0][i]^K[(4*self.roundK-16)+i]
			R[0][i]=R[0][i]^K[(4*self.roundK-12)+i]
		R[0]=R[0]^L[0]
		for k in range(1,self.roundK+1):
			FF=FEAL.F(self,R[k-1],[K[2*(k-1)],K[2*(k-1)+1]])
			R[k]=L[k-1]^FF
			L[k]=R[k-1]
		L[self.round]=L[self.round]^R[self.round]
		for i in range(4):
			R[self.round][i]=R[self.round][i]^K[(4*self.roundK-8)+i]
			L[self.round][i]=L[self.round][i]^K[(4*self.roundK-4)+i]
		C.extend(R[self.round])
		C.extend(L[self.round])
		return C

	def decryptBlock(self,P,K):
		R=np.zeros((self.round+1,4), dtype=int)
		L=np.zeros((self.round+1,4), dtype=int)
		C=[]
		R[0]=[P[0],P[1],P[2],P[3]]
		L[0]=[P[4],P[5],P[6],P[7]]
		K1=K[0:4*self.roundK-16]
		K1.reverse()
		for i in range(4):
			R[0][i]=R[0][i]^K[(4*self.roundK-8)+i]
			L[0][i]=L[0][i]^K[(4*self.roundK-4)+i]
		L[0]=L[0]^R[0]
		for k in range(1,self.roundK+1):
			FF=FEAL.F(self,L[k-1],[K1[2*(k-1)+1],K1[2*(k-1)]])
			L[k]=R[k-1]^FF
			R[k]=L[k-1]
		R[self.round]=R[self.round]^L[self.round]
		for i in range(4):
			L[self.round][i]=L[self.round][i]^K[(4*self.roundK-16)+i]
			R[self.round][i]=R[self.round][i]^K[(4*self.roundK-12)+i]
		C.extend(L[self.round])
		C.extend(R[self.round])
		return C

	def encryptText(self,Txt,K0):
		K=FEAL.roundKeyGen(self,K0)
		if len(Txt)%self.block==0:
			BlocksN = len(Txt)//self.block
		else:
			BlocksN = len(Txt)//self.block+1
		Txt = Txt.ljust(BlocksN*self.block,(chr(0)))
		ByteTxt = Txt.encode("latin-1")
		IntTxtBlocks=np.zeros((BlocksN,self.block), dtype=int)
		OutInt = []
		for i in range(BlocksN):
			for j in range(self.block):
				IntTxtBlocks[i][j]=ByteTxt[j+8*i]
			OutInt.extend(FEAL.encryptBlock(self,IntTxtBlocks[i], K))
		return OutInt, ' '.join(str(hex(n)) for n in OutInt)

	def decryptText(self,OutInt,K0):
		K=FEAL.roundKeyGen(self,K0)
		DecInt=[]
		IntBlocks=np.zeros((len(OutInt)//self.block,self.block), dtype=int)
		i=0
		for j in range(len(OutInt)//self.block):
			IntBlocks[j]=OutInt[i:i+self.block]
			DecInt.extend(FEAL.decryptBlock(self,IntBlocks[j],K))
			i+=self.block
		return DecInt,(bytes(DecInt).decode("latin-1")).rstrip(chr(0))

if __name__ == "__main__":
	Txt=open('Text.txt',mode='r',encoding="latin-1").read()
	chif=FEAL(8)
	K0=open('Key.txt',mode='r',encoding="latin-1").read().split()
	OutInt,OutTxt=chif.encryptText(Txt,K0)
	open('TextEncryp.txt',mode='w',encoding="latin-1").write(OutTxt)
	#время выполнения
	print("Время выполнения: %s сек" % (time.time() - start_time))
	DInt, DTxt=chif.decryptText(OutInt,K0)
	open('TextDecryp.txt',mode='w',encoding="latin-1").write(DTxt)
	#время выполнения
	print("Время выполнения: %s сек" % (time.time() - start_time))
