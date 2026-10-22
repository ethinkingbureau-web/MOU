import re,sys,shutil,os,zipfile
src='x/word/document.xml'
d=open(src,encoding='utf8').read()
assert '{' not in d
ps=re.findall(r'<w:p[ >].*?</w:p>',d,flags=re.S)
TRE=re.compile(r'<w:t(?: [^>]*)?>([^<]*)</w:t>')
def setp(i,changes):
    p=ps[i]; idx=[0]
    def rep(m):
        k=idx[0]; idx[0]+=1
        if k in changes:
            return '<w:t xml:space="preserve">%s</w:t>'%changes[k]
        return m.group(0)
    new=TRE.sub(rep,p)
    ps[i]=new
Q='&quot;'
setp(4,{0:'This MEMORANDUM OF UNDERSTANDING (%sMOU%s) is made on {effDate}'%(Q,Q),1:'',2:'',3:'',4:'',5:'',6:' (the %sEffective Date%s).'%(Q,Q)})
setp(5,{2:'下称“本MOU”）于{effDateCn}',3:'',4:'（'})
setp(14,{0:'{partnerName}{partnerDescEn}',1:' (hereinafter referred to as %sParty B%s).'%(Q,Q),2:'',3:''})
setp(15,{0:'{partnerNameCn}{partnerDescCn}（以下简称“乙方”）。'})
setp(24,{2:" Pavilion at Party A's "})
setp(87,{1:'',2:'{termEn}',3:', renewable by mutual agreement. Either Party may ',4:'terminate with {noticeDays}',5:''})
setp(88,{1:'{termYears}',2:'年，经双方协商可续期。任何一方可提前{noticeDays}日发出通知终止本备忘录。'})
# apply paragraph changes
out=d
orig=re.findall(r'<w:p[ >].*?</w:p>',d,flags=re.S)
pos=0; res=[]
for o,n in zip(orig,ps):
    j=out.index(o,pos); res.append(out[pos:j]); res.append(n); pos=j+len(o)
res.append(out[pos:]); out=''.join(res)

# signature block -> borderless two-column table
def para(t,bold=False):
    rp='<w:rPr><w:rFonts w:hint="eastAsia"/>'+('<w:b/>' if bold else '')+'</w:rPr>'
    return '<w:p><w:pPr><w:spacing w:before="0" w:after="60"/></w:pPr><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'%(rp,t) if t else '<w:p><w:pPr><w:spacing w:before="0" w:after="60"/></w:pPr></w:p>'
LINE='_'*25
KN='<w:keepNext/>'
def para(t,kn=True):
    return '<w:p><w:pPr>'+('<w:keepNext/>' if kn else '')+'<w:spacing w:before="0" w:after="60"/></w:pPr>'+('<w:r><w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'%t if t else '')+'</w:p>'
def cell(t,kn=True):
    return '<w:tc><w:tcPr><w:tcW w:w="2500" w:type="pct"/><w:tcMar><w:left w:w="0" w:type="dxa"/><w:right w:w="240" w:type="dxa"/></w:tcMar></w:tcPr>'+para(t,kn)+'</w:tc>'
def row(l,r,kn=True):
    return '<w:tr><w:trPr><w:cantSplit/></w:trPr>'+cell(l,kn)+cell(r,kn)+'</w:tr>'
rows=[('',''),('CHINA-ASEAN MERCANTILE EXCHANGE','{partnerName}'),('',''),(LINE,LINE),('Signature  签名','Signature  签名'),('',''),(LINE,LINE),
 ('Name 姓名: {aName}','Name 姓名: {bName}'),('Title 职务: {aTitle}','Title 职务: {bTitle}'),('Date 日期: {aDate}','Date 日期: {bDate}')]
TBL=('<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblInd w:w="100" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblLook w:val="0000"/></w:tblPr>'
 '<w:tblGrid><w:gridCol w:w="4500"/><w:gridCol w:w="4500"/></w:tblGrid>'+''.join(row(*r,kn=(i<len(rows)-1)) for i,r in enumerate(rows))+'</w:tbl>')
a=out.index(orig[123]); z=out.index(orig[133])+len(orig[133])
out=out[:a]+TBL+out[z:]
# keep the execution block together on one page
def keep(pxml):
    if '<w:keepNext/>' in pxml: return pxml
    if '<w:pPr>' in pxml:
        return re.sub(r'(<w:pPr>(?:<w:pStyle [^>]*/>)?)',r'\1<w:keepNext/>',pxml,count=1)
    return re.sub(r'(<w:p(?: [^>]*)?>)',r'\1<w:pPr><w:keepNext/></w:pPr>',pxml,count=1)
for i in (118,119,121,122):
    assert not re.sub(r'<[^>]+>','',orig[i]).strip() and 'sectPr' not in orig[i] and '<w:br' not in orig[i]
    out=out.replace(orig[i],'',1)
for i in (114,115,116,117,120):
    out=out.replace(orig[i],keep(orig[i]),1)
# replace the 11 blank paragraphs before Appendix A with a real page break
a2=out.index(orig[134]); z2=out.index(orig[145])
gap=out[a2:z2]
assert '<w:t' not in gap and 'sectPr' not in gap and '<w:br' not in gap
pb=orig[145]
pb2=re.sub(r'(<w:pPr>(?:<w:pStyle [^>]*/>)?)',r'\1<w:pageBreakBefore/>',pb,count=1) if '<w:pPr>' in pb else re.sub(r'(<w:p(?: [^>]*)?>)',r'\1<w:pPr><w:pageBreakBefore/></w:pPr>',pb,count=1)
out=out[:a2]+pb2+out[z2+len(pb):]
# country
out=out.replace('Vietnam','{country}').replace('越南','{countryCn}')
assert 'Vietnam' not in re.sub(r'<[^>]+>','',out), re.findall('.{20}Vietnam.{20}',out)
# appendix table
tbl=re.findall(r'<w:tbl>.*?</w:tbl>',out,flags=re.S)[-1]
rows=re.findall(r'<w:tr[ >].*?</w:tr>',tbl,flags=re.S)
keys=['Name','Title','Email','Phone']
newtbl=tbl
for r,k in zip(rows[1:5],keys):
    tcs=list(re.finditer(r'<w:tc>.*?</w:tc>',r,flags=re.S))
    nr=r
    for tc,pre in ((tcs[1],'a'),(tcs[2],'b')):
        t=tc.group(0)
        t2=re.sub(r'(<w:p [^>]*>.*?</w:pPr>)(</w:p>)',lambda m:m.group(1)+'<w:r><w:t xml:space="preserve">{%sC%s}</w:t></w:r>'%(pre,k)+m.group(2),t,count=1,flags=re.S)
        assert t2!=t
        nr=nr.replace(t,t2)
    newtbl=newtbl.replace(r,nr)
out=out.replace(tbl,newtbl)
open('x/word/document.xml','w',encoding='utf8').write(out)
print(sorted(set(re.findall(r'\{(\w+)\}',out))))
