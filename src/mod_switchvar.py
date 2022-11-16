import numpy as np 

def ssh2rv(ssh, lon=None, lat=None, xac=None):

    
    if len(lon.shape) == 1 and len(lat.shape) == 1:
        lon,lat = np.meshgrid(lon,lat)
    
    g = 9.81 
    f = 4*np.pi/86164*np.sin(lat*np.pi/180)
    ssh_shapelen = len(ssh.shape)
    dx,dy = lonlat2dxdy(lon,lat) 
    
    
        
    if ssh_shapelen == 2:
        _dx = dx[1:-1,1:-1]
        _dy = dy[1:-1,1:-1]
    elif ssh_shapelen == 3:
        ssh = np.moveaxis(ssh, 0, -1)
        f = f[:,:,np.newaxis]
        _dx = dx[1:-1,1:-1,np.newaxis]
        _dy = dy[1:-1,1:-1,np.newaxis]

    # Initialization
    rv = np.zeros_like(ssh)*np.nan
    # Compute relative vorticity
    rv[1:-1,1:-1] = g/f[1:-1,1:-1] *\
        ((ssh[2:,1:-1]+ssh[:-2,1:-1]-2*ssh[1:-1,1:-1])/_dy**2 \
        +(ssh[1:-1,2:]+ssh[1:-1,:-2]-2*ssh[1:-1,1:-1])/_dx**2)
    if xac is not None:
        rv = _masked_edge(rv, xac)

    if ssh_shapelen == 3:
        rv = np.moveaxis(rv, -1, 0)

    return rv
 

def ssh2uv(Ht,lon,lat):
    dlon = lon[1]-lon[0]
    dlat = lat[1]-lat[0]
    
    if len(lon.shape)==2:
        lon2 = lon
        lat2 = lat
    else:
        lon2,lat2 = np.meshgrid(lon,lat)
    deg2m=110000.
    fc = 2*2*np.pi/86164*np.sin(lat2*np.pi/180)
    Ugt = 0*Ht
    Vgt = 0*Ht

    for t in range(Ht.shape[0]): 
        Vgt[1:-1,1:-1] = 9.81/fc[1:-1,1:-1]*(Ht[1:-1,2:]-Ht[1:-1,:-2])/(2*np.diff(lon2,axis=1)[1:-1,1:]*deg2m*np.cos(lat2[1:-1,1:-1]*np.pi/180.))
        Ugt[1:-1,1:-1] = -9.81/fc[1:-1,1:-1]*(Ht[2:,1:-1]-Ht[:-2,1:-1])/(2*np.diff(lat2,axis=0)[1:,1:-1]*deg2m)

    return np.sqrt(Ugt**2+Vgt**2)


def lonlat2dxdy(lon,lat):
    dlon = np.gradient(lon)
    dlat = np.gradient(lat)
    dx = np.sqrt((dlon[1]*111000*np.cos(np.deg2rad(lat)))**2
                 + (dlat[1]*111000)**2)
    dy = np.sqrt((dlon[0]*111000*np.cos(np.deg2rad(lat)))**2
                 + (dlat[0]*111000)**2)
    dx[0,:] = dx[1,:]
    dx[-1,: ]= dx[-2,:] 
    dx[:,0] = dx[:,1]
    dx[:,-1] = dx[:,-2]
    dy[0,:] = dy[1,:]
    dy[-1,:] = dy[-2,:] 
    dy[:,0] = dy[:,1]
    dy[:,-1] = dy[:,-2]
    
    return dx,dy